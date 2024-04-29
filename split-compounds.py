from collections import defaultdict
import sys

def create_word_frequency_dict(filename):
    """
    Reads a file containing tab-separated lines with word, tag, and lemma,
    and returns a frequency dictionary of proper nouns excluding numbers.

    Parameters:
        filename (str): The path to the input file.

    Returns:
        dict: A dictionary where keys are proper nouns and values are their frequencies.
    """
    freq_dict = defaultdict(int)

    with open(filename, 'r', encoding='utf-8') as source:
        for line in source:
            if line != "\n":
                cleaned_line = line.strip("\n")
                word, tag, lemma = cleaned_line.split("\t")
                if tag == "NN" and word[0].isupper() and word[1:].islower() and not word.isdigit():
                    freq_dict[word] += 1

    return freq_dict


def split_compound(word, freq_dict, subwords=None):
    """
    Splits a compound word into its constituent parts based on a frequency dictionary.

    Parameters:
        word (str): The compound word to split.
        freq_dict (dict): A frequency dictionary where keys are words and values are their frequencies.
        subwords (list, optional): A list containing parts of the compound word (used internally for recursion).

    Yields:
        list: A list of lists containing constituent parts of the compound word.
    """
    if subwords is None:
        subwords = []

    if word in freq_dict:
        yield subwords + [word]

    for i in range(3, len(word) - 2):
        if (word[:i]).capitalize() in freq_dict.keys() and len(word[:i]) >= 3:
            if word[i] == "s" and i < len(word) - 3:
                yield from split_compound((word[i + 1:]).capitalize(), freq_dict, subwords + [word[:i]])
            yield from split_compound((word[i:]).capitalize(), freq_dict, subwords + [word[:i]])


def geometric_mean(freq_dict):
    """
    Calculates the geometric mean of compound words based on a frequency dictionary and returns each word
    with its subwords an their geometric mean

    Parameters:
        freq_dict (dict): A dictionary containing word frequencies.

    Prints:
        str: Original word, geometric mean, and split compound words in descending order of mean values.
    """
    for original_word, frequency in freq_dict.items():
        # Generate a list of compound word splits for the current word
        split_compound_list = list(split_compound(original_word, freq_dict))

        geometric_means = []
        # Iterate through each split compound word
        for word_list in split_compound_list:
            # Calculate the product of frequencies of individual words in the split
            product = 1
            for word in word_list:
                word_freq = freq_dict[word]
                product *= word_freq
            # Calculate the geometric mean for the split
            geometric_mean = product ** (1 / len(word_list))
            geometric_means.append((word_list, geometric_mean))

        sorted_geometric_means = sorted(geometric_means, key=lambda x: x[1], reverse=True)
        for word_list, mean_value in sorted_geometric_means:
            string_word_list = " ".join(word_list)
            print(original_word + " " + str(mean_value) + " " + string_word_list)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python split-compounds.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    freq_dict = create_word_frequency_dict(filename)
    geometric_mean(freq_dict)
