# --- 9. Οδηγοί ---
from flask import Blueprint, flash, render_template, request, redirect, url_for
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action 

# Δημιουργία του Blueprint
drivers_bp = Blueprint('drivers', __name__)

@drivers_bp.route('/drivers')
def drivers():
    conn = get_db_connection()
    
    # Ταξινόμηση
    sort_by = request.args.get('sort', 'col_new')
    order = request.args.get('order', 'asc')
    
    # Χάρτης για ασφάλεια (να μην περάσει κανείς SQL injection στο sort)
    valid_columns = {'col_new': 'col_new', 'col_old': 'col_old', 'name': 'name'}
    sort_column = valid_columns.get(sort_by, 'col_new')
    
    # Έξυπνη ταξινόμηση αριθμών (CAST)
    if sort_column in ['col_new', 'col_old']:
        sql_order = f"CAST({sort_column} AS INTEGER) {order}, {sort_column} {order}"
    else:
        sql_order = f"{sort_column} {order}"
        
    query = f"SELECT * FROM drivers ORDER BY {sql_order}"
    drivers_list = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('drivers.html', drivers=drivers_list, sort_by=sort_by, order=order)

# --- 10. Προσθήκη Οδηγού ---
@drivers_bp.route('/add_driver', methods=['POST'])
def add_driver():
    conn = get_db_connection()
    col_new = request.form.get('new_code', '').strip() # Προσοχή: στο HTML το λες new_code
    col_old = request.form.get('old_code', '').strip() # Προσοχή: στο HTML το λες old_code
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if name:
        try:
            conn.execute('INSERT INTO drivers (col_new, col_old, name, phone) VALUES (?, ?, ?, ?)',
                         (col_new, col_old, name, phone))
            conn.commit()
            flash('Ο οδηγός προστέθηκε!')
        except Exception as e:
            flash(f'Σφάλμα κατά την προσθήκη: {e}')
    else:
        flash('Το όνομα είναι υποχρεωτικό!')
        
    conn.close()
    return redirect(url_for('drivers'))

# --- 11. Επεξεργασία Οδηγού ---
@drivers_bp.route('/edit_driver/<int:driver_id>', methods=['GET', 'POST'])
def edit_driver(driver_id):
    conn = get_db_connection()
    if request.method == 'POST':
        col_new = request.form.get('new_code', '').strip()
        col_old = request.form.get('old_code', '').strip()
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        conn.execute('UPDATE drivers SET col_new=?, col_old=?, name=?, phone=? WHERE id=?',
                     (col_new, col_old, name, phone, driver_id))
        conn.commit()
        conn.close()
        flash('Τα στοιχεία του οδηγού ενημερώθηκαν!')
        return redirect(url_for('drivers'))
        
    driver = conn.execute('SELECT * FROM drivers WHERE id=?', (driver_id,)).fetchone()
    conn.close()
    
    # Πρέπει να περάσουμε τα ονόματα πεδίων όπως τα περιμένει το template edit_driver.html
    # Αν το edit_driver.html χρησιμοποιεί d['col_new'], τότε ΟΚ.
    return render_template('edit_driver.html', driver=driver)

# --- 12. Διαγραφή Οδηγού ---
@drivers_bp.route('/delete_driver/<int:driver_id>', methods=['POST'])
def delete_driver(driver_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM drivers WHERE id = ?', (driver_id,))
    conn.commit()
    conn.close()
    flash('Ο οδηγός διαγράφηκε.')
    return redirect(url_for('drivers'))