import re
import sys
from os.path import isfile

from bf.bloom_filter import BloomFilter

DEFAULT_WORD_LIST = '/usr/share/dict/words'

# A simple application of the bloom filter: load a word list, store it in a filter, and spell-check
# a different file against it.


def tokenize(in_file):
    """Iterates over words in `in_file`. Returns continuous alphanumeric strings, lowercased."""
    if not isfile(in_file):
        raise RuntimeError(f"Can't open {in_file}")

    with open(in_file) as fp:
        for line in fp:
            for word in re.sub(r'[^a-z0-9_]', ' ', line).split():
                yield word.lower()


def spellcheck(in_file, word_list_file):
    # TODO: consider first counting the number of words in the file, to better estimate the filter parameters.
    bf = BloomFilter(50000, 0.001)

    for word in tokenize(word_list_file):
        bf.add(word)

    for word in tokenize(in_file):
        if word not in bf:
            print(word)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file-to-spellcheck> [word-list] (default: {DEFAULT_WORD_LIST})")
        print("Both file-to-spellcheck and word-list are assumed case-insensitive, whitespace-delimited")
        print("Outputs to stdout every word in <file-to-spellcheck> that is not found in word-list, one word per line.")
        raise RuntimeError

    word_list_file = DEFAULT_WORD_LIST if len(sys.argv) < 3 else sys.argv[2]
    spellcheck(sys.argv[1], word_list_file)
