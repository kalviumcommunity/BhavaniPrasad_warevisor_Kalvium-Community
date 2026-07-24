import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def setup_db():
    db_path = 'data/assignment.db'
    os.makedirs('data', exist_ok=True)
    
    # Remove existing db if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        customer_type TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_date TIMESTAMP,
        customer_id INTEGER,
        order_id INTEGER,
        amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP,
        email_verified_at TIMESTAMP,
        first_purchase_at TIMESTAMP
    )
    ''')

    # Generate Mock Data
    np.random.seed(42)
    
    # Customers
    num_customers = 50
    customers_data = []
    for i in range(1, num_customers + 1):
        c_type = np.random.choice(['Enterprise', 'SMB', 'Individual'], p=[0.2, 0.5, 0.3])
        customers_data.append((i, c_type))
        
    cursor.executemany('INSERT INTO customers VALUES (?, ?)', customers_data)
    
    # Transactions
    num_transactions = 200
    transactions_data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400)
    
    for i in range(1, num_transactions + 1):
        days_offset = np.random.randint(0, 400)
        t_date = start_date + timedelta(days=days_offset)
        c_id = np.random.randint(1, num_customers + 1)
        o_id = i + 1000 # dummy order id
        amount = round(np.random.uniform(10.0, 500.0), 2)
        transactions_data.append((t_date.strftime('%Y-%m-%d %H:%M:%S'), c_id, o_id, amount))
        
    cursor.executemany('INSERT INTO transactions (transaction_date, customer_id, order_id, amount) VALUES (?, ?, ?, ?)', transactions_data)
    
    # Users
    num_users = 100
    users_data = []
    u_start_date = end_date - timedelta(days=100)
    
    for i in range(1, num_users + 1):
        days_offset = np.random.randint(0, 100)
        c_date = u_start_date + timedelta(days=days_offset)
        
        # Email verification
        ev_date = None
        if np.random.rand() > 0.2: # 80% verify email
            ev_date = c_date + timedelta(hours=np.random.randint(1, 48))
            
        # First purchase
        fp_date = None
        if ev_date and np.random.rand() > 0.3: # 70% of verified make purchase
            fp_date = ev_date + timedelta(days=np.random.randint(1, 10))
            
        users_data.append((
            c_date.strftime('%Y-%m-%d %H:%M:%S'),
            ev_date.strftime('%Y-%m-%d %H:%M:%S') if ev_date else None,
            fp_date.strftime('%Y-%m-%d %H:%M:%S') if fp_date else None
        ))
        
    cursor.executemany('INSERT INTO users (created_at, email_verified_at, first_purchase_at) VALUES (?, ?, ?)', users_data)
    
    conn.commit()
    conn.close()
    print("Database setup complete with mock data!")

if __name__ == "__main__":
    setup_db()
