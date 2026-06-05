"""Unit tests for canonicalization utilities."""

import unittest

from src.core.canonicalize import (
    canonicalize_json,
    canonicalize_text,
    compute_checksum,
    compute_deterministic_seed,
)


class TestCanonicalize(unittest.TestCase):
    def test_canonicalize_json_order_independent(self):
        a = {"b": 1, "a": 2}
        b = {"a": 2, "b": 1}
        self.assertEqual(canonicalize_json(a), canonicalize_json(b))

    def test_canonicalize_text_normalization(self):
        s = "line1\r\nline2  \rline3\n"
        normalized = canonicalize_text(s)
        self.assertNotIn("\r", normalized)
        self.assertTrue(normalized.startswith("line1"))
        self.assertFalse(normalized.endswith(" "))

    def test_compute_checksum_str_and_bytes(self):
        hex1 = compute_checksum("hello")
        hex2 = compute_checksum(b"hello")
        self.assertEqual(hex1, hex2)
        self.assertEqual(len(hex1), 64)

    def test_deterministic_seed_order_independence(self):
        sources1 = {"a.txt": "content A", "b.txt": "content B"}
        sources2 = {"b.txt": "content B", "a.txt": "content A"}
        s1 = compute_deterministic_seed(sources1)
        s2 = compute_deterministic_seed(sources2)
        self.assertEqual(s1, s2)

    def test_unicode_and_special_chars(self):
        sources = {"u.txt": "emoji: 😊, accents: éü, special: \t \n \r"}
        seed = compute_deterministic_seed(sources)
        # deterministic hex
        self.assertEqual(len(seed), 64)

    def test_repeated_runs_are_identical(self):
        sources = {"a": "x", "b": "y"}
        seeds = {compute_deterministic_seed(sources) for _ in range(100)}
        self.assertEqual(len(seeds), 1)

    def test_empty_inputs_and_checksum_none(self):
        # canonicalize empty structures
        self.assertEqual(canonicalize_json({}), "{}")
        # checksum of None should be valid hex length
        checksum = compute_checksum(None)
        self.assertEqual(len(checksum), 64)

    def test_seed_changes_when_source_changes(self):
        sources_a = {"file1.txt": "content A", "file2.txt": "content B"}
        sources_b = {"file1.txt": "content A", "file2.txt": "content B modified"}
        seed_a = compute_deterministic_seed(sources_a)
        seed_b = compute_deterministic_seed(sources_b)
        self.assertNotEqual(seed_a, seed_b)


if __name__ == "__main__":
    unittest.main()
