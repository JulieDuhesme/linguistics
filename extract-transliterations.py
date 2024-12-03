import sys
import numpy as np
from collections import defaultdict

# NoiseModel class handles the estimation of letter probabilities for source and target languages.
class NoiseModel:
    def __init__(self, word_pair_list):
        # Estimate probabilities for source and target letters
        self.src_letter_prob = self.estimate_probabilities(word_pair_list, 0)
        self.tgt_letter_prob = self.estimate_probabilities(word_pair_list, 1)

    def estimate_probabilities(self, word_pair_list, index):
        # Count occurrences of each letter in the specified index (0 for source, 1 for target)
        letter_counts = defaultdict(int)
        total_letters = 0
        for pair in word_pair_list:
            for letter in pair[index]:
                letter_counts[letter] += 1
                total_letters += 1
        # Calculate the probability of each letter
        letter_prob = {letter: count / total_letters for letter, count in letter_counts.items()}
        return letter_prob

    def word_pair_prob(self, src_word, tgt_word):
        # Calculate the probability of the word pair by multiplying individual letter probabilities
        src_prob = np.prod([self.src_letter_prob.get(letter, 1e-6) for letter in src_word])
        tgt_prob = np.prod([self.tgt_letter_prob.get(letter, 1e-6) for letter in tgt_word])
        return src_prob * tgt_prob

# TransliterationModel class handles the estimation and reestimation of transliteration probabilities.
class TransliterationModel:
    def __init__(self, src_letters, tgt_letters):
        # Initialize the transliteration unit probabilities uniformly
        self.trans_unit_prob = self.initialize_trans_unit_prob(src_letters, tgt_letters)
        self.trans_unit_freq = defaultdict(float)

    def initialize_trans_unit_prob(self, src_letters, tgt_letters):
        # Initialize uniform probability for each possible transliteration unit
        N = len(src_letters) + 1
        M = len(tgt_letters) + 1
        initial_prob = 1 / (N * M - 1)
        trans_unit_prob = defaultdict(lambda: initial_prob)
        return trans_unit_prob

    def add_freq(self, src_letter, tgt_letter, freq):
        # Add the frequency to the transliteration unit frequency dictionary
        self.trans_unit_freq[(src_letter, tgt_letter)] += freq

    def reestimate(self):
        # Reestimate probabilities based on frequencies
        total_freq = sum(self.trans_unit_freq.values())
        for unit in self.trans_unit_freq:
            self.trans_unit_prob[unit] = self.trans_unit_freq[unit] / total_freq

# MiningModel class combines NoiseModel and TransliterationModel and performs EM algorithm.
class MiningModel:
    def __init__(self, word_pair_list, num_iterations=3):
        # Extract all unique letters from the word pairs for initialization
        src_letters = set(letter for pair in word_pair_list for letter in pair[0])
        tgt_letters = set(letter for pair in word_pair_list for letter in pair[1])
        self.noise_model = NoiseModel(word_pair_list)
        self.trans_model = TransliterationModel(src_letters, tgt_letters)
        self.trans_prior = 0.5
        self.trans_freq = 0
        self.num_iterations = num_iterations

    def estimate_freqs(self, word_pair_list):
        # Estimate frequencies using forward-backward algorithm
        for src_word, tgt_word in word_pair_list:
            alpha = self.forward(src_word, tgt_word)
            beta = self.backward(src_word, tgt_word)
            p_trans = alpha[-1, -1]
            p_noise = self.noise_model.word_pair_prob(src_word, tgt_word)
            p_trans_pair = self.trans_prior * p_trans / (self.trans_prior * p_trans + (1 - self.trans_prior) * p_noise)
            self.trans_freq += p_trans_pair
            for i in range(1, len(src_word) + 1):
                for j in range(1, len(tgt_word) + 1):
                    trans_pair = (src_word[i-1], tgt_word[j-1])
                    expected_count = p_trans_pair * alpha[i-1, j-1] * self.trans_model.trans_unit_prob[trans_pair] * beta[i, j] / p_trans
                    self.trans_model.add_freq(*trans_pair, expected_count)

    def reestimate_probs(self, word_pair_list):
        # Reestimate transliteration probabilities and the prior probability of transliteration
        self.trans_model.reestimate()
        self.trans_prior = self.trans_freq / len(word_pair_list)

    def forward(self, src_word, tgt_word):
        # Forward algorithm to calculate alpha values
        len_src = len(src_word)
        len_tgt = len(tgt_word)
        alpha = np.zeros((len_src + 1, len_tgt + 1))
        alpha[0, 0] = 1
        for i in range(1, len_src + 1):
            alpha[i, 0] = alpha[i-1, 0] * self.trans_model.trans_unit_prob[(src_word[i-1], '')]
        for j in range(1, len_tgt + 1):
            alpha[0, j] = alpha[0, j-1] * self.trans_model.trans_unit_prob[('', tgt_word[j-1])]
        for i in range(1, len_src + 1):
            for j in range(1, len_tgt + 1):
                alpha[i, j] = (alpha[i-1, j] * self.trans_model.trans_unit_prob[(src_word[i-1], '')] +
                               alpha[i, j-1] * self.trans_model.trans_unit_prob[('', tgt_word[j-1])] +
                               alpha[i-1, j-1] * self.trans_model.trans_unit_prob[(src_word[i-1], tgt_word[j-1])])
        return alpha

    def backward(self, src_word, tgt_word):
        # Backward algorithm to calculate beta values
        len_src = len(src_word)
        len_tgt = len(tgt_word)
        beta = np.zeros((len_src + 1, len_tgt + 1))
        beta[len_src, len_tgt] = 1
        for i in range(len_src - 1, -1, -1):
            beta[i, len_tgt] = beta[i+1, len_tgt] * self.trans_model.trans_unit_prob[(src_word[i], '')]
        for j in range(len_tgt - 1, -1, -1):
            beta[len_src, j] = beta[len_src, j+1] * self.trans_model.trans_unit_prob[('', tgt_word[j])]
        for i in range(len_src - 1, -1, -1):
            for j in range(len_tgt - 1, -1, -1):
                beta[i, j] = (beta[i+1, j] * self.trans_model.trans_unit_prob[(src_word[i], '')] +
                              beta[i, j+1] * self.trans_model.trans_unit_prob[('', tgt_word[j])] +
                              beta[i+1, j+1] * self.trans_model.trans_unit_prob[(src_word[i], tgt_word[j])])
        return beta

    def em(self, word_pair_list):
        # Expectation-Maximization algorithm to train the model
        for _ in range(self.num_iterations):
            self.trans_model.trans_unit_freq = defaultdict(float)
            self.trans_freq = 0
            self.estimate_freqs(word_pair_list)
            self.reestimate_probs(word_pair_list)

    def print_transliterations(self, word_pair_list):
        #Print pairs where the transliteration probability is greater than 0.5
        for src_word, tgt_word in word_pair_list:
            alpha = self.forward(src_word, tgt_word)
            p_trans = alpha[-1, -1]
            p_noise = self.noise_model.word_pair_prob(src_word, tgt_word)
            p_trans_pair = self.trans_prior * p_trans / (self.trans_prior * p_trans + (1 - self.trans_prior) * p_noise)
            if p_trans_pair > 0.5:
                print(f"{src_word} -> {tgt_word}")

# Function to load word pairs from a file
def load_word_pairs(file_path):
    word_pairs = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            src_word, tgt_word = line.strip().split()
            word_pairs.append((src_word, tgt_word))
    return word_pairs

if __name__ == "__main__":
    word_pair_file = sys.argv[1]
    word_pair_list = load_word_pairs(word_pair_file)
    model = MiningModel(word_pair_list, num_iterations=3)
    model.em(word_pair_list)
    model.print_transliterations(word_pair_list)
