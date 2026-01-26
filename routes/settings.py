# --- 2. Σελίδα Ρυθμίσεων ---
from flask import Blueprint, flash, render_template, request, redirect, url_for, jsonify
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action, set_setting, default_credits_for_dest 

# Δημιουργία του Blueprint
settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    conn = get_db_connection()
    
    if request.method == 'POST' and 'save_rates' in request.form:
        for key in request.form:
            if key.startswith('rate_'):
                parts = key.split('_')
                h_id = parts[1]
                d_id = parts[2]
                val = int(float(request.form[key] or 0))
                conn.execute('INSERT OR REPLACE INTO rates (hotel_id, dest_id, credits) VALUES (?, ?, ?)',
                             (h_id, d_id, val))
        conn.commit()
        flash('Οι τιμές αποθηκεύτηκαν!')
        return redirect(url_for('settings.settings'))
    
    hotel_mode = get_setting('hotel_sort_mode')
    dest_mode = get_setting('dest_sort_mode')
    h_order = 'name' if hotel_mode == 'alpha' else 'sort_order, name'
    d_order = 'name' if dest_mode == 'alpha' else 'sort_order, name'
    
    hotels = conn.execute(f'SELECT * FROM hotels WHERE is_active=1 ORDER BY {h_order}').fetchall()
    destinations = conn.execute(f'SELECT * FROM destinations WHERE is_active=1 ORDER BY {d_order}').fetchall()
    
    rates_rows = conn.execute('SELECT * FROM rates').fetchall()
    rates_dict = {}
    for r in rates_rows:
        rates_dict[(r['hotel_id'], r['dest_id'])] = int(r['credits'])
        
    conn.close()
    return render_template('settings.html', hotels=hotels, destinations=destinations,
                           rates=rates_dict, hotel_mode=hotel_mode, dest_mode=dest_mode)

# --- 2. Διαχείριση Ξενοδοχείων ---
@settings_bp.route('/manage_hotels', methods=['POST'])
def manage_hotels():
    conn = get_db_connection()
    if 'new_hotel_name' in request.form:
        name = request.form['new_hotel_name'].strip()
        if name:
            max_order = conn.execute('SELECT MAX(sort_order) as m FROM hotels WHERE is_active=1').fetchone()['m'] or 0
            existing = conn.execute('SELECT id FROM hotels WHERE name=?', (name,)).fetchone()
            
            if existing:
                conn.execute('UPDATE hotels SET is_active=1, sort_order=? WHERE id=?', (max_order + 1, existing['id']))
                hotel_id = existing['id']
            else:
                conn.execute('INSERT INTO hotels (name, sort_order, is_active) VALUES (?, ?, 1)', (name, max_order + 1))
                hotel_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            
            dests = conn.execute("SELECT id, name FROM destinations WHERE is_active=1").fetchall()
            for d in dests:
                default_val = default_credits_for_dest(d["name"])
                conn.execute("INSERT OR IGNORE INTO rates (hotel_id, dest_id, credits) VALUES (?, ?, ?)", (hotel_id, d["id"], default_val))

    if 'delete_hotel_id' in request.form:
        h_id = request.form['delete_hotel_id']
        conn.execute('UPDATE hotels SET is_active=0 WHERE id=?', (h_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('settings.settings'))

# --- 3. Διαχείριση Προορισμών ---
@settings_bp.route('/manage_destinations', methods=['POST'])
def manage_destinations():
    conn = get_db_connection()
    if 'new_dest_name' in request.form:
        name = request.form['new_dest_name'].strip()
        if name:
            max_order = conn.execute('SELECT MAX(sort_order) as m FROM destinations WHERE is_active=1').fetchone()['m'] or 0
            existing = conn.execute('SELECT id FROM destinations WHERE name=?', (name,)).fetchone()
            
            if existing:
                conn.execute('UPDATE destinations SET is_active=1, sort_order=? WHERE id=?', (max_order + 1, existing['id']))
                dest_id = existing['id']
            else:
                conn.execute('INSERT INTO destinations (name, sort_order, is_active) VALUES (?, ?, 1)', (name, max_order + 1))
                dest_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
            
            hotels = conn.execute("SELECT id FROM hotels WHERE is_active=1").fetchall()
            default_val = default_credits_for_dest(name)
            for h in hotels:
                conn.execute("INSERT OR IGNORE INTO rates (hotel_id, dest_id, credits) VALUES (?, ?, ?)", (h["id"], dest_id, default_val))

    if 'delete_dest_id' in request.form:
        d_id = request.form['delete_dest_id']
        conn.execute('UPDATE destinations SET is_active=0 WHERE id=?', (d_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('settings.settings'))

# --- 4. Ταξινόμηση ---
@settings_bp.route('/toggle_sort/<item_type>')
def toggle_sort(item_type):
    if item_type == 'hotels':
        current = get_setting('hotel_sort_mode')
        new_mode = 'alpha' if current == 'custom' else 'custom'
        set_setting('hotel_sort_mode', new_mode)
    elif item_type == 'destinations':
        current = get_setting('dest_sort_mode')
        new_mode = 'alpha' if current == 'custom' else 'custom'
        set_setting('dest_sort_mode', new_mode)
    return redirect(url_for('settings.settings'))

# --- 5. Reorder ---
@settings_bp.route('/reorder/<item_type>', methods=['POST'])
def reorder(item_type):
    conn = get_db_connection()
    new_order = request.json.get('order', [])
    table = 'hotels' if item_type == 'hotels' else 'destinations'
    for idx, item_id in enumerate(new_order):
        conn.execute(f'UPDATE {table} SET sort_order=? WHERE id=?', (idx, item_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})
