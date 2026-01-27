import sqlite3


DB_PATH = "taxi.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# --- READ ---
def get_all_services():
    """Επιστρέφει λίστα για τον Πίνακα 1 (Service History)"""
    query = """
    SELECT 
        s.id, s.service_date, s.odometer_km, s.workshop_name, 
        ROUND(COALESCE(SUM(sl.line_total), 0) + s.labor_cost, 2) as total_cost
    FROM services s
    LEFT JOIN service_lines sl ON s.id = sl.service_id
    GROUP BY s.id
    ORDER BY s.service_date DESC, s.odometer_km DESC
    """
    with get_db() as conn:
        return conn.execute(query).fetchall()


def get_parts_history():
    """Επιστρέφει λίστα για τον Πίνακα 2 (Parts History)"""
    query = """
    SELECT sl.service_id, s.service_date, sl.part_description
    FROM service_lines sl
    JOIN services s ON s.id = sl.service_id
    ORDER BY s.service_date DESC, sl.id DESC
    """
    with get_db() as conn:
        return conn.execute(query).fetchall()


def get_service_by_id(service_id):
    """Επιστρέφει το service και τις γραμμές του (για Edit)"""
    with get_db() as conn:
        service = conn.execute("SELECT * FROM services WHERE id = ?", (service_id,)).fetchone()
        lines = conn.execute("SELECT * FROM service_lines WHERE service_id = ?", (service_id,)).fetchall()
    return service, lines


# --- WRITE (Transaction handled automatically by 'with conn:') ---
def create_service(data, lines):
    with get_db() as conn:
        cur = conn.cursor()
        # 1. Insert Header
        cur.execute("""
            INSERT INTO services (service_date, odometer_km, workshop_name, labor_cost, note)
            VALUES (?, ?, ?, ?, ?)
        """, (data['date'], data['km'], data['workshop'], data['labor'], data['note']))
        
        service_id = cur.lastrowid
        
        # 2. Insert Lines
        for line in lines:
            line_total = line['qty'] * line['price']
            cur.execute("""
                INSERT INTO service_lines (service_id, part_code, part_description, qty, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (service_id, line['code'], line['desc'], line['qty'], line['price'], line_total))
            
    return service_id


def update_service(service_id, data, lines):
    with get_db() as conn:
        # 1. Update Header
        conn.execute("""
            UPDATE services 
            SET service_date=?, odometer_km=?, workshop_name=?, labor_cost=?, note=?
            WHERE id=?
        """, (data['date'], data['km'], data['workshop'], data['labor'], data['note'], service_id))
        
        # 2. Delete OLD lines (easier than diffing)
        conn.execute("DELETE FROM service_lines WHERE service_id = ?", (service_id,))
        
        # 3. Insert NEW lines
        for line in lines:
            line_total = line['qty'] * line['price']
            conn.execute("""
                INSERT INTO service_lines (service_id, part_code, part_description, qty, unit_price, line_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (service_id, line['code'], line['desc'], line['qty'], line['price'], line_total))


def delete_service(service_id):
    with get_db() as conn:
        conn.execute("DELETE FROM services WHERE id = ?", (service_id,))


# --- WORKSHOPS (Συνεργεία) ---
def get_all_workshops():
    """Επιστρέφει workshops με το όνομα του τύπου τους (JOIN)"""
    query = """
    SELECT w.*, wt.name as type_name 
    FROM workshops w
    LEFT JOIN workshop_types wt ON w.type_id = wt.id
    ORDER BY w.name
    """
    with get_db() as conn:
        return conn.execute(query).fetchall()


def create_workshop(data):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO workshops (name, phone, address, type_id) 
            VALUES (?, ?, ?, ?)
        """, (data['name'], data['phone'], data['address'], data.get('type_id')))


def get_workshop_by_id(id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM workshops WHERE id = ?", (id,)).fetchone()


def update_workshop(id, data):
    with get_db() as conn:
        conn.execute("""
            UPDATE workshops 
            SET name=?, phone=?, address=?, type_id=? 
            WHERE id=?
        """, (data['name'], data['phone'], data['address'], data.get('type_id'), id))


def delete_workshop(id):
    with get_db() as conn:
        conn.execute("DELETE FROM workshops WHERE id = ?", (id,))


# --- WORKSHOP TYPES (Είδη Συνεργείων) ---
def get_all_workshop_types():
    with get_db() as conn:
        return conn.execute("SELECT * FROM workshop_types ORDER BY name").fetchall()


def create_workshop_type(name):
    with get_db() as conn:
        try:
            conn.execute("INSERT INTO workshop_types (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError:
            pass  # Αγνοούμε αν υπάρχει ήδη


# --- SPARE PARTS (Ανταλλακτικά - Κατάλογος) ---
def get_all_parts_registry():
    with get_db() as conn:
        return conn.execute("SELECT * FROM spare_parts ORDER BY description").fetchall()


def create_part_registry(data):
    with get_db() as conn:
        conn.execute("INSERT INTO spare_parts (code, description, notes) VALUES (?, ?, ?)",
                     (data['code'], data['description'], data['notes']))


def get_part_registry_by_id(id):
    with get_db() as conn:
        return conn.execute("SELECT * FROM spare_parts WHERE id = ?", (id,)).fetchone()


def update_part_registry(id, data):
    with get_db() as conn:
        conn.execute("UPDATE spare_parts SET code=?, description=?, notes=? WHERE id=?",
                     (data['code'], data['description'], data['notes'], id))


def delete_part_registry(id):
    with get_db() as conn:
        conn.execute("DELETE FROM spare_parts WHERE id = ?", (id,))

# --- ΠΡΟΣΘΗΚΗ στο services_repo.py ---

def update_workshop_type(id, new_name):
    with get_db() as conn:
        try:
            conn.execute("UPDATE workshop_types SET name = ? WHERE id = ?", (new_name, id))
        except sqlite3.IntegrityError:
            pass # Αγνοούμε αν το όνομα υπάρχει ήδη

def delete_workshop_type(id):
    with get_db() as conn:
        # ΠΡΟΣΟΧΗ: Αν σβήσεις ένα είδος που χρησιμοποιείται, τα συνεργεία θα μείνουν "ορφανά"
        # Μπορείς να βάλεις έλεγχο εδώ ή να αφήσεις την SQLite να το χειριστεί (αν έχεις ON DELETE SET NULL)
        # Εδώ απλά σβήνουμε (και τα συνεργεία θα δείχνουν σε ανύπαρκτο ID ή θα γίνουν NULL αν έχει ρυθμιστεί)
        conn.execute("DELETE FROM workshop_types WHERE id = ?", (id,))
