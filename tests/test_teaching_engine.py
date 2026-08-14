"""
Tests for AI Teaching Engine Interface
"""

import unittest
from ai.teaching_engine import explain_concept

class TestTeachingEngine(unittest.TestCase):
    def test_explain_concept_structure(self):
        result = explain_concept("Binary Search")
        self.assertIn("concept", result)
        self.assertIn("analogy", result)
        self.assertIn("beginner_explanation", result)
        self.assertIn("technical_explanation", result)
        self.assertIn("practical_example", result)
        self.assertEqual(result["concept"], "Binary Search")

if __name__ == "__main__":
    unittest.main()
