"""
Tests for Smart Refresh Interface and Duration Limits
"""

import unittest
from smart_refresh.refresh_engine import start_refresh, MAX_REFRESH_DURATION_SECONDS

class TestSmartRefresh(unittest.TestCase):
    def test_refresh_duration_capped_at_5_minutes(self):
        session = start_refresh()
        self.assertLessEqual(session["max_duration_seconds"], 300)
        self.assertEqual(session["max_duration_seconds"], MAX_REFRESH_DURATION_SECONDS)
        self.assertIn("resume_checkpoint", session)

if __name__ == "__main__":
    unittest.main()
