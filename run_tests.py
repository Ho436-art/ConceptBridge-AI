"""
ConceptBridge AI - Test Runner Script
Executes all database test cases and prints a clean summary.

Usage:
    python run_tests.py
"""

import os
import sys
import unittest
from pathlib import Path

# Enable fast deterministic test mode
os.environ["TESTING"] = "true"

# Add project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
