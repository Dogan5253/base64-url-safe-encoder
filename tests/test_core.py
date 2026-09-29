import unittest

from base64_url_safe_encoder import encode, decode


class TestEncode(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(encode(b""), "")

    def test_one_byte(self):
        # b'\x00' -> standard b64 'AA==' -> url-safe unpadded 'AA'
        self.assertEqual(encode(b"\x00"), "AA")

    def test_two_bytes(self):
        # b'\x00\x00' -> 'AAA=' -> 'AAA'
        self.assertEqual(encode(b"\x00\x00"), "AAA")

    def test_three_bytes_no_padding_needed(self):
        self.assertEqual(encode(b"\x00\x00\x00"), "AAAA")

    def test_uses_url_safe_alphabet(self):
        # 0xfb 0xff 0xbf contains bits that map to '+' and '/' in standard b64.
        # URL-safe alphabet must substitute '-' and '_'.
        result = encode(b"\xfb\xff\xbf")
        self.assertNotIn("+", result)
        self.assertNotIn("/", result)
        self.assertIn("-", result)
        self.assertIn("_", result)

    def test_output_is_str_not_bytes(self):
        self.assertIsInstance(encode(b"abc"), str)

    def test_rejects_non_bytes(self):
        with self.assertRaises(TypeError):
            encode("not bytes")  # type: ignore[arg-type]


class TestDecode(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(decode(""), b"")

    def test_decode_unpadded(self):
        self.assertEqual(decode("AA"), b"\x00")
        self.assertEqual(decode("AAA"), b"\x00\x00")

    def test_decode_padded(self):
        self.assertEqual(decode("AA=="), b"\x00")
        self.assertEqual(decode("AAA="), b"\x00\x00")

    def test_decode_accepts_bytes_input(self):
        self.assertEqual(decode(b"AA"), b"\x00")

    def test_round_trip(self):
        for payload in [b"", b"a", b"ab", b"abc", b"abcd", b"\x00\xff" * 10]:
            self.assertEqual(decode(encode(payload)), payload)

    def test_decode_url_safe_alphabet(self):
        self.assertEqual(decode("-_"), b"\xfb")

    def test_decode_rejects_standard_alphabet_chars(self):
        with self.assertRaises(ValueError):
            decode("a+b")
        with self.assertRaises(ValueError):
            decode("a/b")

    def test_decode_rejects_non_ascii(self):
        with self.assertRaises(ValueError):
            decode("héllo")

    def test_decode_rejects_non_string_non_bytes(self):
        with self.assertRaises(TypeError):
            decode(123)  # type: ignore[arg-type]

    def test_decode_rejects_invalid_length_after_padding(self):
        # Length 1 cannot be padded to a valid multiple of four in a way that
        # produces a sensible decode; base64 requires at least 2 chars.
        with self.assertRaises(ValueError):
            decode("A")


if __name__ == "__main__":
    unittest.main()
