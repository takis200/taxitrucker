from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, Response
import sqlite3
from datetime import datetime, timedelta
import io
import csv
import logging
import services_repo
from logging.handlers import TimedRotatingFileHandler
import os
from utils import get_db_connection, get_setting, log_action, set_setting, default_credits_for_dest
from routes.main import main_bp

# --- ΚΩΔΙΚΑΣ LOGGING (ΑΡΧΗ) ---
if not os.path.exists('logs'):
    os.makedirs('logs')

def log_action(message):
    try:
        current_month = datetime.now().strftime('%Y-%m')
        filename = f"logs/activity_{current_month}.txt"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        print(f"Log Error: {e}")
# --- ΚΩΔΙΚΑΣ LOGGING (ΤΕΛΟΣ) ---

app = Flask(__name__)
app.secret_key = 'super_secret_key'
DB_NAME = "taxi.db"

# --- ΠΡΟΣΘΕΣΤΕ ΕΔΩ ΤΑ BLUEPRINT ---
from routes.main import main_bp  # 1. Εισαγωγή
app.register_blueprint(main_bp)  # 2. Εγγραφή
from routes.settings import settings_bp  # 1. Εισαγωγή
app.register_blueprint(settings_bp)      # 2. Εγγραφή
from routes.drivers import drivers_bp  # 1. Εισαγωγή
app.register_blueprint(drivers_bp)      # 2. Εγγραφή
from routes.services import services_bp  # 1. Εισαγωγή
app.register_blueprint(services_bp)      # 2. Εγγραφή
from routes.credits import credits_bp  # 1. Εισαγωγή
app.register_blueprint(credits_bp)      # 2. Εγγραφή
from routes.exportrates import exportrates_bp  # 1. Εισαγωγή
app.register_blueprint(exportrates_bp)      # 2. Εγγραφή
from routes.history import history_bp  # 1. Εισαγωγή
app.register_blueprint(history_bp)      # 2. Εγγραφή
# ----------------------------------

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

# Φίλτρο για αλλαγή ημερομηνίας σε Μέρα-Μήνας-Έτος
@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return ""
    try:
        # Μετατροπή από YYYY-MM-DD σε DD-MM-YYYY
        date_obj = datetime.strptime(str(value), '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except ValueError:
        return value  # Αν δεν είναι ημερομηνία, το αφήνουμε όπως είναι

# --- ΤΕΣΤ ΣΥΝΔΕΣΗΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
@app.route('/test')
def test():
    return f"DB OK: {services_repo.get_all_services()}"

print("\n--- Registered Routes ---")
print(app.url_map)
print("-------------------------\n")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
