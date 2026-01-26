from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action 

# Δημιουργία του Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        # 1. Καταχώρηση Διαδρομής
        if 'add_ride' in request.form:
            hotel_id = request.form['hotel']
            dest_id = request.form['destination']
            price = float(request.form['price'] or 0)
            tolls = float(request.form['tolls'] or 0)
            
            h_name = conn.execute('SELECT name FROM hotels WHERE id=?', (hotel_id,)).fetchone()['name']
            d_name = conn.execute('SELECT name FROM destinations WHERE id=?', (dest_id,)).fetchone()['name']
            
            credits_row = conn.execute('SELECT credits FROM rates WHERE hotel_id=? AND dest_id=?', (hotel_id, dest_id)).fetchone()
            credits_val = int(credits_row['credits']) if credits_row else 0
            
            conn.execute('INSERT INTO rides (date, hotel_name, dest_name, price, tolls, credits_charged) VALUES (?,?,?,?,?,?)',
                         (today_str, h_name, d_name, price, tolls, credits_val))
            conn.commit()
            
            # --- ΝΕΟ: ΚΑΤΑΓΡΑΦΗ ---
            log_action(f"ΝΕΑ ΔΙΑΔΡΟΜΗ: {today_str} | {h_name} -> {d_name} | {price}€")
            # ----------------------
            return redirect(url_for('main.index'))

        # 2. Ενημέρωση Apps (+Extras)
        if 'update_apps' in request.form:
            try:
                freenow = float(request.form.get('freenow') or 0)
                uber = float(request.form.get('uber') or 0)
                bolt = float(request.form.get('bolt') or 0)
                extras = float(request.form.get('extras') or 0)
                
                conn.execute('INSERT OR REPLACE INTO app_earnings (date, freenow, uber, bolt, extras) VALUES (?,?,?,?,?)',
                             (today_str, freenow, uber, bolt, extras))
                conn.commit()
            except Exception as e:
                print(f"DEBUG ERROR: {e}")
            return redirect(url_for('main.index'))

        # 3. Ενημέρωση Εξόδων
        if 'update_expenses' in request.form:
            fuel = int(float(request.form['fuel'] or 0))
            misc = float(request.form['misc'] or 0)
            
            conn.execute('INSERT OR REPLACE INTO expenses (date, fuel, misc) VALUES (?,?,?)',
                         (today_str, fuel, misc))
            conn.commit()
            return redirect(url_for('main.index'))

    # Φόρτωση
    hotel_mode = get_setting('hotel_sort_mode')
    order_by = 'name' if hotel_mode == 'alpha' else 'sort_order, name'
    hotels = conn.execute(f'SELECT * FROM hotels WHERE is_active=1 ORDER BY {order_by}').fetchall()
    
    dest_mode = get_setting('dest_sort_mode')
    dest_order = 'name' if dest_mode == 'alpha' else 'sort_order, name'
    destinations = conn.execute(f'SELECT * FROM destinations WHERE is_active=1 ORDER BY {dest_order}').fetchall()
    
    todays_rides = conn.execute('SELECT * FROM rides WHERE date=?', (today_str,)).fetchall()
    apps = conn.execute('SELECT * FROM app_earnings WHERE date=?', (today_str,)).fetchone()
    expenses = conn.execute('SELECT * FROM expenses WHERE date=?', (today_str,)).fetchone()
    
    # Υπολογισμοί
    total_ride_income = sum(r['price'] for r in todays_rides)
    total_tolls = sum(r['tolls'] for r in todays_rides)
    total_credits_units = sum(r['credits_charged'] for r in todays_rides)
    credits_cost_money = total_credits_units * 0.5
    
    if apps:
        app_extras = apps['extras'] if 'extras' in apps.keys() and apps['extras'] else 0
        app_income = apps['freenow'] + apps['uber'] + apps['bolt'] + app_extras
    else:
        app_income = 0
        
    fuel_cost = expenses['fuel'] if expenses else 0
    misc_cost = expenses['misc'] if expenses else 0
    total_expenses = fuel_cost + misc_cost
    
    total_revenue = total_ride_income + app_income
    net_profit = total_revenue - total_tolls - credits_cost_money - total_expenses
    
    conn.close()
    
    return render_template('index.html', 
                           hotels=hotels, destinations=destinations, rides=todays_rides,
                           apps=apps, expenses=expenses,
                           profit=net_profit, revenue=total_revenue,
                           tolls=total_tolls, credits_money=credits_cost_money,
                           fuel=fuel_cost, misc=misc_cost)

# --- 15. Βοηθητικά (API/Ajax) ---
@main_bp.route('/get_credits')
def get_credits():
    h_id = request.args.get('hotel')
    d_id = request.args.get('dest')
    conn = get_db_connection()
    res = conn.execute('SELECT credits FROM rates WHERE hotel_id=? AND dest_id=?', (h_id, d_id)).fetchone()
    conn.close()
    return jsonify({'credits': int(res['credits']) if res else 0})