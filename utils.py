import sqlite3
import os
from datetime import datetime

DB_NAME = "taxi.db"

# --- Συναρτήσεις Βάσης Δεδομένων & Ρυθμίσεων ---

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_setting(key, default='custom'):
    conn = get_db_connection()
    result = conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    conn.close()
    return result['value'] if result else default

def set_setting(key, value):
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# --- Logging ---

def log_action(message):
    try:
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        current_month = datetime.now().strftime('%Y-%m')
        filename = f"logs/activity_{current_month}.txt"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        print(f"Log Error: {e}")

# --- Default Credits for Destinations ---
DEFAULT_CREDITS = {
    "Αεροδρόμιο": 10,
    "Λιμάνι Πειραιά": 5,
    "Λιμάνι Ραφήνας": 10,
    "Λιμάνι Λαυρίου": 10,
    "Αττική": 3,
}

def default_credits_for_dest(dest_name: str) -> int:
    return int(DEFAULT_CREDITS.get(dest_name, 0))
