import unittest
import os
import sys
import sqlite3

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

class TestIntegrity(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_integrity.db"
        self.original_db = database.DB_NAME
        database.DB_NAME = self.test_db
        database.init_db()

    def tearDown(self):
        database.DB_NAME = self.original_db
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except:
                pass

    def test_duplicate_barcode(self):
        # Already has barcode 101 from seed
        with self.assertRaises(Exception) as cm:
            database.add_product("New Apple", "101", "Fruits", 2.0, 50)
        self.assertIn("already exists", str(cm.exception))

    def test_duplicate_username(self):
        # Already has username admin from seed
        with self.assertRaises(Exception) as cm:
            database.add_user("New Admin", "admin", "9999", "admin")
        self.assertIn("already exists", str(cm.exception))

    def test_duplicate_pin(self):
        # Already has pin 1111 from seed
        with self.assertRaises(Exception) as cm:
            database.add_user("New User", "newuser", "1111", "cashier")
        self.assertIn("already exists", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
