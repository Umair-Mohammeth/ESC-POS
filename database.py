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
        price REAL NOT NULL,
        stock_quantity INTEGER DEFAULT 0
    )
    ''')
    
    # Transactions Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL,
        cashier_id INTEGER,
        items_json TEXT, -- Storing sold items as JSON string for simplicity [ {id, name, price, qty}, ... ]
        FOREIGN KEY (cashier_id) REFERENCES users (id)
    )
    ''')
    
    # Seed default users if empty
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            ('Admin User', '1111', 'admin'),
            ('Manager User', '2222', 'manager'),
            ('Cashier User', '3333', 'cashier'),
            ('Stocker User', '4444', 'stocker')
        ]
        cursor.executemany("INSERT INTO users (name, pin, role) VALUES (?, ?, ?)", users)
        print("Default users created.")

    # Seed some sample products if empty
    cursor.execute("SELECT count(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            ('Apple', '101', 1.50, 100),
            ('Banana', '102', 0.80, 150),
            ('Milk', '103', 3.50, 50),
            ('Bread', '104', 2.00, 40),
            ('Eggs (Dozen)', '105', 4.00, 30),
            ('Soda', '106', 1.25, 200)
        ]
        cursor.executemany("INSERT INTO products (name, barcode, price, stock_quantity) VALUES (?, ?, ?, ?)", products)
        print("Sample products created.")
        
    conn.commit()
    conn.close()

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
    # Search by name or barcode
    sql = "SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ?"
    cursor.execute(sql, (f'%{query}%', f'%{query}%'))
    products = cursor.fetchall()
    conn.close()
    return [dict(row) for row in products]

def create_transaction(cashier_id, items, total_amount):
    """
    items: list of dicts {id, name, price, qty}
    Returns transaction_id or raises Exception
    """
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Deduct stock
        for item in items:
            cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (item['id'],))
            current_stock = cursor.fetchone()['stock_quantity']
            if current_stock < item['qty']:
                raise Exception(f"Insufficient stock for {item['name']}")
            
            new_stock = current_stock - item['qty']
            cursor.execute("UPDATE products SET stock_quantity = ? WHERE id = ?", (new_stock, item['id']))
        
        # Record Transaction
        items_json = json.dumps(items)
        cursor.execute("INSERT INTO transactions (total_amount, cashier_id, items_json) VALUES (?, ?, ?)", 
                       (total_amount, cashier_id, items_json))
        
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

    conn.close()
    return [dict(row) for row in rows]

# Admin Helpers - Products
def add_product(name, barcode, price, stock):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, barcode, price, stock_quantity) VALUES (?, ?, ?, ?)", 
                   (name, barcode, price, stock))
    conn.commit()
    conn.close()

def update_product(id, name, barcode, price, stock):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name=?, barcode=?, price=?, stock_quantity=? WHERE id=?", 
                   (name, barcode, price, stock, id))
    conn.commit()
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

def add_user(name, pin, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, pin, role) VALUES (?, ?, ?)", (name, pin, role))
    conn.commit()
    conn.close()

def update_user(id, name, pin, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=?, pin=?, role=? WHERE id=?", (name, pin, role, id))
    conn.commit()
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
