import math

import pyhash

from bf.simple_bit_array import SimpleBitArray


class BloomFilter:
    """
    See https://en.wikipedia.org/wiki/Bloom_filter.

    General comments:

    - The underlying data is stored in memory, as a bit array (implemented separately, in the SimpleBitArray class).
      For larger bloom filters -- where the expected number of items is in the billions -- a file (maybe memory-mapped)
      may be more appropriate.

    - There's no native Python bit array so I implemented a simple one with limited functionality. For the hash
      function, however, I'm using an external library.

    - Potential extensions:
      - Support persistence by storing and loading the filter to a file. This would entail simply storing the
        class-level data (e.g., number of hashes) as well as the bit array.
      - Debug mode: supply a flag at construction that makes the filter store internal data (such as items added)
        and allows examining its state.
      - Additional configurability in overriding the number of hashes or number of bits used, to adjust performance.
      - Operations on the filter: intersection, union.
      - LRU caching.
      - Lots of additional possible functionality: counting (deletable) filters, adjustable bit arrays, and more.
    """

    def __init__(self, num_items, fp_rate=0.01):
        """
        Create a bloom filter.
        I chose to have the caller supply the expected number of items and the false positive rate, as these are the
        highest-level constraints. An alternative, or addition, would be to supply the maximum amount of memory allowed,
        and then derive the best false positive rate that can be supported.

        :param num_items: The expected number of items that will be added to the filter.
        :param fp_rate: The allowed false positive rate (items reported in the set, although they were not added to it).
        """
        if num_items < 1:
            raise ValueError("num_items must be positive.")

        if not (0 < fp_rate < 1):
            raise ValueError("fp_rate must be between 0 and 1.")

        self.num_bits = self._estimate_num_bits(num_items, fp_rate)
        self.num_hashes = self._estimate_num_hashes(fp_rate)

        # Non-cryptographic, fast hash function that can use different seeds.
        self.hasher = pyhash.fnv1_32()

        # The underlying bit array.
        self.bit_array = SimpleBitArray(self.num_bits)

        # The actual number of items stored. Needed for len().
        self.num_items_stored = 0

    def __contains__(self, item):
        for ha in self._hashes(item):
            if not self.bit_array.test(ha):
                return False
        return True

    def __len__(self):
        return self.num_items_stored

    @staticmethod
    def _estimate_num_bits(n, p):
        # Taken from https://en.wikipedia.org/wiki/Bloom_filter#Optimal_number_of_hash_functions
        return int(-n * math.log(p) / math.log(2) ** 2)

    @staticmethod
    def _estimate_num_hashes(p):
        # Taken from https://en.wikipedia.org/wiki/Bloom_filter#Optimal_number_of_hash_functions
        return int(-math.ceil(math.log2(p)))

    def _hashes(self, item):
        # Iterate over the hashes of `item`.
        for i in range(self.num_hashes):
            yield self.hasher(item, seed=i) % self.num_bits

    def add(self, item):
        """Add `item` to the filter."""
        for ha in self._hashes(item):
            self.bit_array.set(ha)
        self.num_items_stored += 1
