from collections import defaultdict
import sys

def create_frequency_dict(filename):
    """
    Reads a corpus file and returns a frequency dictionary.

    Parameters:
        filename (str): The path to the input file.

    Returns:
        dict: A dictionary where keys are words and values are their frequencies.
    """
    frequency_dict = defaultdict(int)

    with open(filename, 'r', encoding='utf-8') as source:
        for line in source:
            if line.strip():  # Skip empty lines
                word, _, _ = line.strip().split("\t")
                frequency_dict[word] += 1

    return frequency_dict

def find_anagrams(frequency_dict):
    """
    Finds anagrams from a frequency dictionary.

    Parameters:
        frequency_dict (dict): A dictionary where keys are words and values are their frequencies.

    Returns:
        dict: A dictionary where keys are alphabetically sorted anagrams and values are lists of words formed from them.
    """
    anagram_dict = defaultdict(list)
    for word, _ in frequency_dict.items():
        sorted_word = ''.join(sorted(word.lower()))
        if word not in anagram_dict[sorted_word]:
            anagram_dict[sorted_word].append(word)

    return anagram_dict

def print_anagrams(anagram_dict, frequency_dict):
    """
    Prints and filters anagrams from an anagram dictionary.

    Parameters:
        anagram_dict (dict): A dictionary where keys are alphabetically sorted anagrams and values are lists of words formed from them.
        frequency_dict (dict): A dictionary where keys are words and values are their frequencies.
    """
    for anagram, words in anagram_dict.items():
        # Filter words based on frequency, absence of hyphens, and containing only letters
        filtered_words = [word for word in words if frequency_dict.get(word, 0) >= 10 and '-' not in word and word.isalpha()]

        # Remove duplicates
        for word1 in filtered_words:
            for word2 in filtered_words:
                if word1.lower() == word2.lower() and word1 != word2:
                    tup1 = frequency_dict[word1]
                    tup2 = frequency_dict[word2]
                    if tup1 > tup2:
                        filtered_words.remove(word2)
                    else:
                        filtered_words.remove(word1)

        # Print sorted words
        if len(filtered_words) > 1:
            sorted_words = sorted(filtered_words, key=lambda x: frequency_dict[x], reverse=True)
            print(' '.join(sorted_words))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python anagramme.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    frequency_dict = create_frequency_dict(filename)
    anagram_dict = find_anagrams(frequency_dict)
    print_anagrams(anagram_dict, frequency_dict)


