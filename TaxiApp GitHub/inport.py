import sqlite3

DB_NAME = "taxi.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# 1. Πίνακας Συνεργείων
cursor.execute("""
CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT
);
""")

# 2. Πίνακας Ανταλλακτικών (Registry)
cursor.execute("""
CREATE TABLE IF NOT EXISTS spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    description TEXT NOT NULL,
    notes TEXT
);
""")

conn.commit()
conn.close()
print("✅ Οι πίνακες workshops και spare_parts δημιουργήθηκαν επιτυχώς!")
