"""
Tests for AI Teaching Engine Interface
"""

import unittest
from ai.teaching_engine import explain_concept
from models.schemas import ConceptExplanation

class TestTeachingEngine(unittest.TestCase):
    def test_explain_concept_structure(self):
        result = explain_concept("Binary Search")
        # Test object attribute access
        self.assertEqual(result.concept, "Binary Search")
        self.assertTrue(len(result.real_world_analogy) > 0)
        self.assertTrue(len(result.simple_explanation) > 0)
        
        # Test dictionary-like access
        self.assertIn("concept", result)
        self.assertIn("analogy", result)
        self.assertIn("beginner_explanation", result)
        self.assertIn("technical_explanation", result)
        self.assertIn("practical_example", result)
        self.assertEqual(result["concept"], "Binary Search")

if __name__ == "__main__":
    unittest.main()
