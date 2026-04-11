import sqlite3
import os
from datetime import datetime

DB_NAME = "pos_system.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT UNIQUE,
        pin TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'cashier', 'stocker'))
    )
    ''')
    
    # Products Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        barcode TEXT UNIQUE,
        category TEXT DEFAULT 'General',
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0
    )
    ''')
    
    # Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        subtotal REAL NOT NULL,
        discount_amount REAL DEFAULT 0,
        total_amount REAL NOT NULL,
        cashier_id INTEGER,
        items_json TEXT,
        FOREIGN KEY (cashier_id) REFERENCES users (id)
    )
    ''')

    # Discounts Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS discounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        type TEXT CHECK(type IN ('percentage', 'fixed')) NOT NULL,
        value REAL NOT NULL,
        min_amount REAL DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )
    ''')

    # User Logs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Idempotent Migrations

    # Check for columns in transactions
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'subtotal' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN subtotal REAL DEFAULT 0")
        print("Added subtotal column to transactions table.")
    if 'discount_amount' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN discount_amount REAL DEFAULT 0")
        print("Added discount_amount column to transactions table.")

    # Check for columns in users
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'username' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users (username)")
        print("Added username column to users table.")

    # Check for columns in products
    cursor.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT 'General'")
        print("Added category column to products table.")

    # Seed default discounts
    cursor.execute("SELECT count(*) FROM discounts")
    if cursor.fetchone()[0] == 0:
        discount_seeds = [
            ('SAVE10', 'percentage', 10, 50),
            ('WELCOME20', 'percentage', 20, 0),
            ('FLAT5', 'fixed', 5, 20)
        ]
        cursor.executemany("INSERT INTO discounts (code, type, value, min_amount) VALUES (?, ?, ?, ?)", discount_seeds)
        print("Sample discounts created.")
    
    # Seed default users if empty
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ('Admin User', 'admin', '1111', 'admin'),
            ('Manager User', 'manager', '2222', 'manager'),
            ('Cashier User', 'cashier', '3333', 'cashier'),
            ('Stocker User', 'stocker', '4444', 'stocker')
        ]
        cursor.executemany("INSERT INTO users (name, username, pin, role) VALUES (?, ?, ?, ?)", users)
        print("Default users created.")

    # Seed some sample products if empty
    cursor.execute("SELECT count(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Apple', '101', 'Fruits', 1.50, 100),
            ('Banana', '102', 'Fruits', 0.80, 150),
            ('Milk', '103', 'Dairy', 3.50, 50),
            ('Bread', '104', 'Bakery', 2.00, 40),
            ('Eggs (Dozen)', '105', 'Dairy', 4.00, 30),
            ('Soda', '106', 'Beverages', 1.25, 200)
        ]
        cursor.executemany("INSERT INTO products (name, barcode, category, price, stock_quantity) VALUES (?, ?, ?, ?, ?)", products)
        print("Sample products created.")
        
    conn.commit()
    conn.close()

def get_product_by_id(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return dict(product) if product else None

def get_product_by_barcode(barcode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barcode,))
    product = cursor.fetchone()
    conn.close()
    if product:
        return dict(product)
    return None

def search_products(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Search by name, barcode, or category
    sql = "SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? OR category LIKE ?"
    cursor.execute(sql, (f'%{query}%', f'%{query}%', f'%{query}%'))
    products = cursor.fetchall()
    conn.close()
    return [dict(row) for row in products]

def get_discount(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM discounts WHERE code = ? AND is_active = 1", (code.upper(),))
    discount = cursor.fetchone()
    conn.close()
    return dict(discount) if discount else None

def create_transaction(cashier_id, items, subtotal, discount_amount, total_amount):
    """
    items: list of dicts {id, name, price, qty}
    Returns transaction_id or raises Exception
    """
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Use IMMEDIATE transaction for stock deduction to prevent race conditions
        cursor.execute("BEGIN IMMEDIATE")

        # Deduct stock
        for item in items:
            if item.get('id', 0) > 0:
                cursor.execute("SELECT stock_quantity, name FROM products WHERE id = ?", (item['id'],))
                row = cursor.fetchone()
                if not row:
                    raise Exception(f"Product ID {item['id']} not found")
                if row['stock_quantity'] < item['qty']:
                    raise Exception(f"Insufficient stock for {row['name']} (Available: {row['stock_quantity']})")

                cursor.execute("UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?", (item['qty'], item['id']))
        
        # Record Transaction
        items_json = json.dumps(items)
        cursor.execute('''
            INSERT INTO transactions (subtotal, discount_amount, total_amount, cashier_id, items_json) 
            VALUES (?, ?, ?, ?, ?)
        ''', (subtotal, discount_amount, total_amount, cashier_id, items_json))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return [dict(row) for row in products]

def update_product_stock(product_id, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?", (quantity, product_id))
    conn.commit()
    conn.close()

def get_transactions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, u.name as cashier_name 
        FROM transactions t 
        LEFT JOIN users u ON t.cashier_id = u.id 
        ORDER BY t.date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_daily_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date(date) as day, sum(total_amount) as total 
        FROM transactions 
        GROUP BY day 
        ORDER BY day DESC LIMIT 7
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# User Logs
def log_user_action(user_id, action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_logs (user_id, action) VALUES (?, ?)", (user_id, action))
    conn.commit()
    conn.close()

def get_user_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.*, u.name as user_name 
        FROM user_logs l 
        LEFT JOIN users u ON l.user_id = u.id 
        ORDER BY l.timestamp DESC
    ''')
    logs = cursor.fetchall()
    conn.close()
    return [dict(row) for row in logs]

# Admin Helpers - Products
def add_product(name, barcode, category, price, stock):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, barcode, category, price, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                       (name, barcode, category, price, stock))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_product(id, name, barcode, category, price, stock):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE products SET name=?, barcode=?, category=?, price=?, stock_quantity=? WHERE id=?",
                       (name, barcode, category, price, stock, id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_product(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (id,))
    conn.commit()
    conn.close()

# Admin Helpers - Users
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [dict(row) for row in users]

def add_user(name, username, pin, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, username, pin, role) VALUES (?, ?, ?, ?)", (name, username, pin, role))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_user(id, name, username, pin, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET name=?, username=?, pin=?, role=? WHERE id=?", (name, username, pin, role, id))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
