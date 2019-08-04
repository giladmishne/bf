import sys
import unittest
from time import time

from bf.bloom_filter import BloomFilter
from bf.simple_bit_array import SimpleBitArray


class Test(unittest.TestCase):

    @staticmethod
    def create_bloom_filter(num_items, fp_rate):
        """Creates a filter with the elements [1, 2, 3, ..., `num_items`] (as strings)."""
        bf = BloomFilter(num_items, fp_rate)
        for i in range(1, num_items + 1):
            bf.add(str(i))
        return bf

    def test_set_membership(self):
        num_items = 100
        bf = self.create_bloom_filter(num_items, 0.0001)
        for i in range(1, num_items + 1):
            self.assertTrue(str(i) in bf)

    def check_fp_rate(self, expected_fp_rate):
        num_items = 5000
        bf = self.create_bloom_filter(num_items, expected_fp_rate)
        fp = 0
        for i in range(num_items):
            # The filter contains only strings made of digits, so alpha ones shouldn't be in it
            if 'x' + str(i) in bf:
                fp += 1
        observed_fp_rate = float(fp) / num_items
        # the observed rate should be less than 50% higher than the expected rate.
        self.assertLessEqual(observed_fp_rate / expected_fp_rate, 1.5)

    def test_fp_rate(self):
        for fp_rate in (0.001, 0.01, 0.1, 0.2):
            self.check_fp_rate(fp_rate)

    def test_performance(self):
        # Doesn't actually assert anything, but prints a performance report.
        for num_items in (1000, 50000):
            for fp_rate in (0.01, 0.0001):
                start = time()
                bf = self.create_bloom_filter(num_items, fp_rate)
                for i in range(num_items // 10):
                    _ = str(i) in bf and 'x' + str(i) not in bf
                elapsed = time() - start
                sys.stderr.write(f'items={num_items}\tfp={fp_rate}:\t{elapsed:.3f} sec\n')

    def test_failure(self):
        # zero items
        self.assertRaises(ValueError, self.create_bloom_filter, 0, 0.5)
        # fp_rate is 0
        self.assertRaises(ValueError, self.create_bloom_filter, 1, 0)
        # fp_rate is 1
        self.assertRaises(ValueError, self.create_bloom_filter, 1, 1)

    def test_bit_array(self):
        for n in (12, 17, 50):
            for pos in range(n):
                ba = SimpleBitArray(n)
                ba.set(pos)
                self.assertEqual(ba.count(), 1)
                for i in range(n):
                    # All positions should be unset, except for `pos`.
                    should_be_set = i == pos
                    self.assertEqual(ba.test(i), should_be_set)

        ba = SimpleBitArray(10)
        self.assertEqual(ba.count(), 0)
        for i in range(10):
            ba.set(i)
            self.assertEqual(ba.count(), i + 1)

    def test_bit_array_repr(self):
        ba = SimpleBitArray(16)
        self.assertEqual(str(ba), '00000000|00000000')
        ba.set(0)
        self.assertEqual(str(ba), '00000001|00000000')
        ba.set(10)
        self.assertEqual(str(ba), '00000001|00000100')


if __name__ == '__main__':
    unittest.main()
