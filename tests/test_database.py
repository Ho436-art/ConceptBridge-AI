"""
Tests for Database Initialization and CRUD operations
"""

import unittest
import os
from database.db import init_db, get_connection
from database.queries import create_user, get_user

TEST_DB = "database/test_conceptbridge.db"

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db(TEST_DB)

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_user_creation(self):
        user_id = create_user("testuser", "test@example.com", db_path=TEST_DB)
        self.assertIsNotNone(user_id)
        user = get_user(user_id, db_path=TEST_DB)
        self.assertEqual(user["username"], "testuser")

if __name__ == "__main__":
    unittest.main()
