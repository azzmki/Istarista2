import sqlite3
from config import DATABASE

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                payment_id TEXT,
                amount INTEGER,
                currency TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_payment(user_id, payment_id, amount, currency):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, payment_id, amount, currency)
            VALUES (?, ?, ?, ?)
        ''', (user_id, payment_id, amount, currency))
        conn.commit()

def get_user_payments(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE user_id = ?', (user_id,))
        return cursor.fetchall()