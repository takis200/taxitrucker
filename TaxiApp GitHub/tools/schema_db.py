import sqlite3
import os

DB_NAME = "taxi.db"

def print_schema():
    if not os.path.exists(DB_NAME):
        print(f"❌ Το αρχείο '{DB_NAME}' δεν βρέθηκε.")
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        print(f"--- 📊 SCHEMA ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ: {DB_NAME} ---")
        
        # Λήψη όλων των πινάκων από το σύστημα της SQLite
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        if not tables:
            print("Η βάση είναι κενή (δεν βρέθηκαν πίνακες).")
        
        for name, sql in tables:
            # Αγνοούμε τους εσωτερικούς πίνακες της SQLite
            if name.startswith('sqlite_'):
                continue
                
            print(f"\n🔹 ΠΙΝΑΚΑΣ: {name}")
            print("-" * 40)
            print(sql)
            print("-" * 40)

        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Σφάλμα: {e}")

if __name__ == "__main__":
    print_schema()
