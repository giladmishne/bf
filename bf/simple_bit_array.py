class SimpleBitArray:
    """
    A bit array that only supports the set(), test(), and count() operations.
    Backed by a native bytearray; every byte is used as an 8-bit array.
    """

    def __init__(self, n):
        """
        :param n: The number of bits to store.
        """
        if n < 1:
            raise ValueError("Size must be positive.")
        self.n = n
        n_bytes, leftover = divmod(n, 8)
        if leftover:
            # Need an extra byte to store the leftover bits.
            n_bytes += 1
        self.bytes = bytearray(n_bytes)

    def __str__(self):
        # Show each byte separately as a binary 0/1 string. Example output where three bits are set out of 16:
        # 0001000|10000010
        return '|'.join([f'{byte:08b}' for byte in self.bytes])

    def _get_byte_bit(self, i):
        # Return the byte where `i` is stored in the bytearray, and the bit within that byte.
        if i >= self.n or i < 0:
            raise ValueError(f"Value must be between 0 and {self.n}")
        byte, bit = divmod(i, 8)
        return byte, 1 << bit

    def set(self, pos):
        """Sets position `pos` within the bit array to True."""
        byte, bit = self._get_byte_bit(pos)
        self.bytes[byte] |= bit

    def test(self, pos):
        """Returns True iff `pos` is set within the bit array."""
        byte, bit = self._get_byte_bit(pos)
        return bool(self.bytes[byte] & bit)

    def count(self):
        """Returns the number of bits set."""
        return str(self).count('1')


