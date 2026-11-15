import unittest
from alignment import needleman_wunsch, smith_waterman


class TestGeneWeaver(unittest.TestCase):

    def test_global_identical_sequences(self):
        a1, a2, score = needleman_wunsch("ATCG", "ATCG")
        self.assertEqual(score, 4)
        self.assertEqual(a1, a2)

    def test_global_different_sequences(self):
        a1, a2, score = needleman_wunsch("AAAA", "TTTT")
        self.assertEqual(len(a1), len(a2))
        self.assertEqual(len(a1), 4)

    def test_global_empty_sequences(self):
        a1, a2, score = needleman_wunsch("", "")
        self.assertEqual(score, 0)

    def test_local_identical_sequences(self):
        a1, a2, score = smith_waterman("ATCG", "ATCG")
        self.assertEqual(score, 4)
        self.assertEqual(a1, a2)

    def test_local_matching_region(self):
        a1, a2, score = smith_waterman("AAAATTTT", "GGGGTTTT")
        self.assertEqual(score, 4)
        self.assertEqual(a1, "TTTT")
        self.assertEqual(a2, "TTTT")

    def test_local_empty_sequences(self):
        a1, a2, score = smith_waterman("", "")
        self.assertEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
