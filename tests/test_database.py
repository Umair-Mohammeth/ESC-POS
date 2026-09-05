import unittest
import os
import sqlite3
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_pos.db"
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

    def test_init_db(self):
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM users")
        self.assertGreater(cursor.fetchone()[0], 0)
        conn.close()

    def test_create_transaction(self):
        products = database.get_all_products()
        p = products[0]
        initial_stock = p['stock_quantity']

        items = [{
            'id': p['id'],
            'name': p['name'],
            'price': p['price'],
            'qty': 2,
            'subtotal': p['price'] * 2
        }]

        tid = database.create_transaction(1, items, p['price']*2, 0, p['price']*2)
        self.assertIsNotNone(tid)

        # Check stock deduction
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (p['id'],))
        new_stock = cursor.fetchone()[0]
        self.assertEqual(new_stock, initial_stock - 2)
        conn.close()

    def test_manual_entry_transaction(self):
        items = [{
            'id': 0,
            'name': "Manual Item",
            'price': 10.0,
            'qty': 1,
            'subtotal': 10.0
        }]
        tid = database.create_transaction(1, items, 10.0, 0, 10.0)
        self.assertIsNotNone(tid)

    def test_multiple_manual_entries(self):
        items = [
            {'id': 0, 'name': "Service A", 'price': 50.0, 'qty': 1, 'subtotal': 50.0},
            {'id': 0, 'name': "Part B", 'price': 20.0, 'qty': 1, 'subtotal': 20.0}
        ]
        tid = database.create_transaction(1, items, 70.0, 0, 70.0)
        self.assertIsNotNone(tid)

    def test_insufficient_stock(self):
        products = database.get_all_products()
        p = products[0]

        items = [{
            'id': p['id'],
            'name': p['name'],
            'price': p['price'],
            'qty': p['stock_quantity'] + 1,
            'subtotal': p['price'] * (p['stock_quantity'] + 1)
        }]

        with self.assertRaises(Exception) as cm:
            database.create_transaction(1, items, p['price'], 0, p['price'])
        self.assertIn("Insufficient stock", str(cm.exception))

    def test_empty_barcode_and_username_normalization(self):
        # Multiple products with empty string barcodes should not trigger UNIQUE constraint failure
        database.add_product("Prod 1", "", "General", 10.0, 5)
        database.add_product("Prod 2", "   ", "General", 15.0, 5)

        products = database.get_all_products()
        p1 = [p for p in products if p['name'] == "Prod 1"][0]
        p2 = [p for p in products if p['name'] == "Prod 2"][0]
        self.assertIsNone(p1['barcode'])
        self.assertIsNone(p2['barcode'])

        # Multiple users with empty usernames should also normalize to NULL
        database.add_user("User 1", "", "8888", "cashier")
        database.add_user("User 2", "   ", "9999", "cashier")
        users = database.get_users()
        u1 = [u for u in users if u['name'] == "User 1"][0]
        u2 = [u for u in users if u['name'] == "User 2"][0]
        self.assertIsNone(u1['username'])
        self.assertIsNone(u2['username'])

    def test_get_product_by_barcode_with_empty_input(self):
        self.assertIsNone(database.get_product_by_barcode(""))
        self.assertIsNone(database.get_product_by_barcode("   "))
        self.assertIsNone(database.get_product_by_barcode(None))

if __name__ == '__main__':
    unittest.main()
