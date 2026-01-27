import sqlite3

DB_PATH = "taxi.db"

def update_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("1. Δημιουργία πίνακα workshop_types...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "workshop_types" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "name" TEXT NOT NULL UNIQUE
        );
    """)

    print("2. Εισαγωγή αρχικών δεδομένων...")
    try:
        cursor.executemany("INSERT INTO workshop_types (name) VALUES (?)", 
                           [('Γενικό Συνεργείο',), ('Ηλεκτρολογείο',), 
                            ('Φανοποιείο',), ('Βουλκανιζατέρ',), 
                            ('Ταπετσαρία',), ('Κλιματισμός',)])
    except sqlite3.IntegrityError:
        print("   -> Τα είδη υπάρχουν ήδη, προχωράμε.")

    print("3. Ενημέρωση πίνακα workshops...")
    # Ελέγχουμε αν υπάρχει ήδη η στήλη για να μην χτυπήσει λάθος
    cursor.execute("PRAGMA table_info(workshops)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'type_id' not in columns:
        cursor.execute("ALTER TABLE workshops ADD COLUMN type_id INTEGER REFERENCES workshop_types(id)")
        print("   -> Η στήλη type_id προστέθηκε.")
    else:
        print("   -> Η στήλη type_id υπάρχει ήδη.")

    conn.commit()
    conn.close()
    print("Η αναβάθμιση ολοκληρώθηκε!")

if __name__ == "__main__":
    update_database()
