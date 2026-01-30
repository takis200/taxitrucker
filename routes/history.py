# --- 3. Σελίδα Ιστορικού ---
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action 

# Δημιουργία του Blueprint
history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET', 'POST'])
def history():
    conn = get_db_connection()
    
    today = datetime.now().date()
    default_start = today.strftime('%Y-%m-%d')
    default_end = today.strftime('%Y-%m-%d')
    
    start_date = request.args.get('start_date', default_start)
    end_date = request.args.get('end_date', default_end)
    hotel_filter = request.args.get('hotel', '')
    dest_filter = request.args.get('dest', '')
    
    query = "SELECT * FROM rides WHERE date BETWEEN ? AND ?"
    params = [start_date, end_date]
    
    if hotel_filter:
        query += " AND hotel_name = ?"
        params.append(hotel_filter)
    if dest_filter:
        query += " AND dest_name = ?"
        params.append(dest_filter)
        
    query += " ORDER BY date ASC, id ASC"
    
    rides = conn.execute(query, params).fetchall()
    
    total_ride_income = sum(r['price'] for r in rides)
    total_tolls = sum(r['tolls'] for r in rides)
    total_credits_units = sum(r['credits_charged'] for r in rides)
    total_credits_cost = total_credits_units * 0.5
    
    # Apps Income
    apps_data = conn.execute("""
        SELECT 
            COALESCE(SUM(freenow), 0) as freenow,
            COALESCE(SUM(uber), 0) as uber,
            COALESCE(SUM(bolt), 0) as bolt,
            COALESCE(SUM(extras), 0) as extras
        FROM app_earnings 
        WHERE date BETWEEN ? AND ?
    """, [start_date, end_date]).fetchone()
    
    total_apps_income = (apps_data['freenow'] + apps_data['uber'] + apps_data['bolt'] + apps_data['extras']) if apps_data else 0
    
    apps_breakdown = {
        'freenow': apps_data['freenow'] if apps_data else 0,
        'uber': apps_data['uber'] if apps_data else 0,
        'bolt': apps_data['bolt'] if apps_data else 0,
        'extras': apps_data['extras'] if apps_data else 0
    }
    
    # Expenses
    exp_data = conn.execute("""
        SELECT 
            COALESCE(SUM(fuel), 0) as fuel,
            COALESCE(SUM(misc), 0) as misc
        FROM expenses 
        WHERE date BETWEEN ? AND ?
    """, [start_date, end_date]).fetchone()
    
    total_fuel = exp_data['fuel'] if exp_data else 0
    total_misc = exp_data['misc'] if exp_data else 0
    total_expenses = total_fuel
    
    total_revenue = total_ride_income + total_apps_income
    net_profit = total_revenue - total_tolls - total_credits_cost - total_expenses - total_misc
    
    # Stats
    all_hotels = conn.execute("SELECT DISTINCT hotel_name FROM rides ORDER BY hotel_name").fetchall()
    all_dests = conn.execute("SELECT DISTINCT dest_name FROM rides ORDER BY dest_name").fetchall()
    
    top_hotels = conn.execute("""
        SELECT hotel_name, COUNT(*) as count, SUM(price - tolls - (credits_charged * 0.5)) as profit
        FROM rides WHERE date BETWEEN ? AND ?
        GROUP BY hotel_name ORDER BY count DESC LIMIT 5
    """, [start_date, end_date]).fetchall()
    
    dest_stats = conn.execute("""
        SELECT dest_name, COUNT(*) as count, SUM(price) as total_income, SUM(credits_charged) as total_credits
        FROM rides WHERE date BETWEEN ? AND ?
        GROUP BY dest_name ORDER BY count DESC
    """, [start_date, end_date]).fetchall()
    
    conn.close()
    
    return render_template('history.html', 
                           rides=rides, start_date=start_date, end_date=end_date,
                           hotel_filter=hotel_filter, dest_filter=dest_filter,
                           all_hotels=all_hotels, all_dests=all_dests,
                           total_ride_income=total_ride_income,
                           total_apps_income=total_apps_income,
                           apps_breakdown=apps_breakdown,
                           total_revenue=total_revenue,
                           total_tolls=total_tolls,
                           total_credits_cost=total_credits_cost,
                           total_fuel=total_fuel, total_misc=total_misc, total_expenses=total_expenses,
                           net_profit=net_profit, ride_count=len(rides),
                           top_hotels=top_hotels, dest_stats=dest_stats)

# --- 4. Διαγραφή Διαδρομών ---
@history_bp.route('/delete_ride/<int:ride_id>', methods=['POST'])
def delete_ride(ride_id):
    conn = get_db_connection()
    
    # 1. ΠΡΩΤΑ βρίσκουμε τη διαδρομή για να πάρουμε τα στοιχεία της (πριν σβηστεί!)
    ride_to_delete = conn.execute('SELECT * FROM rides WHERE id = ?', (ride_id,)).fetchone()
    
    if ride_to_delete:
        # 2. Τώρα κάνουμε την ΚΑΤΑΓΡΑΦΗ (Log) όσο έχουμε τα στοιχεία
        # Χρησιμοποιούμε try/except για να μην κρασάρει η εφαρμογή αν κάτι πάει στραβά με το log
        try:
            log_msg = f"ΔΙΑΓΡΑΦΗ: {ride_to_delete['date']} | {ride_to_delete['hotel_name']} -> {ride_to_delete['dest_name']}"
            log_action(log_msg)
        except Exception as e:
            print(f"Log Error: {e}")

        # 3. Τέλος, κάνουμε τη ΔΙΑΓΡΑΦΗ από τη βάση
        conn.execute('DELETE FROM rides WHERE id=?', (ride_id,))
        conn.commit()
    
    conn.close()
    
    # Διαβάζουμε τις ημερομηνίες από το URL (query parameters)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    flash('Η διαδρομή διαγράφηκε!')
    
    # Αν υπάρχουν ημερομηνίες, γυρνάμε στο ιστορικό ΜΕ αυτές
    if start_date and end_date:
        return redirect(url_for('history.history', start_date=start_date, end_date=end_date))
    
    # Αλλιώς γυρνάμε στο απλό ιστορικό (σημερινή μέρα)
    return redirect(url_for('history.history'))

# --- 5. Επεξεργασία Διαδρομών ---
@history_bp.route('/edit_ride/<int:ride_id>', methods=['GET', 'POST'])
def edit_ride(ride_id):
    conn = get_db_connection()
    
    # Φόρτωση δεδομένων
    hotels = conn.execute('SELECT * FROM hotels ORDER BY name').fetchall()
    destinations = conn.execute('SELECT * FROM destinations ORDER BY name').fetchall()
    
    # Παράμετροι ημερομηνιών
    ctx_start = request.args.get('start_date') or request.form.get('ctx_start')
    ctx_end = request.args.get('end_date') or request.form.get('ctx_end')

    if request.method == 'POST':
        # --- ΔΙΟΡΘΩΣΗ: Διαβάζουμε την ΠΑΛΙΑ διαδρομή ΕΔΩ ---
        old_ride = conn.execute('SELECT * FROM rides WHERE id=?', (ride_id,)).fetchone()
        
        # Αν δεν υπάρχει (σπάνιο), φεύγουμε
        if not old_ride:
            conn.close()
            return redirect(url_for('history.history'))

        # Διαβάζουμε τα ΝΕΑ δεδομένα
        new_date = request.form['date']
        hotel_id = request.form['hotel']
        dest_id = request.form['destination']
        price = float(request.form['price'] or 0)
        tolls = float(request.form['tolls'] or 0)
        credits_val = int(float(request.form['credits'] or 0))

        h_row = conn.execute('SELECT name FROM hotels WHERE id=?', (hotel_id,)).fetchone()
        d_row = conn.execute('SELECT name FROM destinations WHERE id=?', (dest_id,)).fetchone()

        if h_row and d_row:
            h_name = h_row['name']
            d_name = d_row['name']
            
            # Ενημέρωση στη βάση
            conn.execute("""
                UPDATE rides SET date=?, hotel_name=?, dest_name=?, price=?, tolls=?, credits_charged=?
                WHERE id=?
            """, (new_date, h_name, d_name, price, tolls, credits_val, ride_id))
            conn.commit()

            # --- LOGGING: Σύγκριση old_ride vs Νέων τιμών ---
            changes = []
            if old_ride['price'] != price:
                changes.append(f"Τιμή: {old_ride['price']}->{price}")
            if old_ride['tolls'] != tolls:
                changes.append(f"Διόδια: {old_ride['tolls']}->{tolls}")
            if old_ride['date'] != new_date:
                changes.append(f"Ημ/νία: {old_ride['date']}->{new_date}")
            if old_ride['hotel_name'] != h_name:
                changes.append(f"Hotel: {old_ride['hotel_name']}->{h_name}")
            if old_ride['dest_name'] != d_name:
                changes.append(f"Προορισμός: {old_ride['dest_name']}->{d_name}")
            
            if changes:
                log_action(f"ΕΠΕΞΕΡΓΑΣΙΑ ID {ride_id}: " + ", ".join(changes))
            else:
                log_action(f"ΕΠΕΞΕΡΓΑΣΙΑ ID {ride_id}: Καμία αλλαγή")
            # ------------------------------------------------

            # flash('Η διαδρομή ενημερώθηκε!')
        
        conn.close()

        # Επιστροφή στο ιστορικό
        if ctx_start and ctx_end:
            return redirect(url_for('history.history', start_date=ctx_start, end_date=ctx_end))
        else:
            return redirect(url_for('history'))

    # Κώδικας για GET (άνοιγμα σελίδας)
    ride = conn.execute('SELECT * FROM rides WHERE id=?', (ride_id,)).fetchone()
    conn.close()

    if ride is None:
        return redirect(url_for('history.history'))

    return render_template('edit_ride.html', ride=ride, hotels=hotels, destinations=destinations, 
                           ctx_start=ctx_start, ctx_end=ctx_end)


# --- 6. Επεξεργασία Apps ---
@history_bp.route('/edit_apps/<date_str>', methods=['GET', 'POST'])
def edit_apps(date_str):
    conn = get_db_connection()
    if request.method == 'POST':
        freenow = float(request.form.get('freenow') or 0)
        uber = float(request.form.get('uber') or 0)
        bolt = float(request.form.get('bolt') or 0)
        extras = float(request.form.get('extras') or 0)
        
        conn.execute('INSERT OR REPLACE INTO app_earnings (date, freenow, uber, bolt, extras) VALUES (?,?,?,?,?)',
                     (date_str, freenow, uber, bolt, extras))
        conn.commit()
        conn.close()
        flash('Τα έσοδα εφαρμογών ενημερώθηκαν!')
        return redirect(url_for('history.history', start_date=date_str, end_date=date_str))

    apps = conn.execute('SELECT * FROM app_earnings WHERE date=?', (date_str,)).fetchone()
    conn.close()
    return render_template('edit_apps.html', apps=apps, date=date_str)

# --- 7. Επεξεργασία Εξόδων ---
@history_bp.route('/edit_expenses/<date_str>', methods=['GET', 'POST'])
def edit_expenses(date_str):
    conn = get_db_connection()
    if request.method == 'POST':
        fuel = float(request.form.get('fuel') or 0)
        misc = float(request.form.get('misc') or 0)
        
        conn.execute('INSERT OR REPLACE INTO expenses (date, fuel, misc) VALUES (?,?,?)',
                     (date_str, fuel, misc))
        conn.commit()
        conn.close()
        flash('Τα έξοδα ενημερώθηκαν!')
        return redirect(url_for('history.history', start_date=date_str, end_date=date_str))

    expenses = conn.execute('SELECT * FROM expenses WHERE date=?', (date_str,)).fetchone()
    conn.close()
    return render_template('edit_expenses.html', expenses=expenses, date=date_str)