from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
import json
import os
import sqlite3
from utils import log_action

airport_bp = Blueprint('airport', __name__, url_prefix='/airport')

# ============================================
# HELPER FUNCTIONS
# ============================================

def sort_flight_time(flight):
    """
    Ταξινόμηση πτήσεων με χρονική λογική.
    Πτήσεις 00:00-05:59 θεωρούνται επόμενης ημέρας και πάνε στο τέλος.
    """
    time_str = flight['est_time']
    try:
        hour, minute = map(int, time_str.split(':'))
        if hour < 6:  # Μεταμεσονύκτιες πτήσεις
            hour += 24
        return hour * 60 + minute
    except:
        return 9999

def load_json_data(filename):
    """Φόρτωση JSON αρχείων από τον φάκελο data/"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Warning: Could not load {filename}: {e}")
        return {}

def load_api_key():
    """Φόρτωση API key από το airlabs.env"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        key_path = os.path.join(base_dir, 'api', 'airlabs.env')
        with open(key_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ CRITICAL: Could not load API key: {e}")
        return None

def get_db_connection():
    """Σύνδεση με τη βάση δεδομένων"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'taxi.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# DATA LOADING
# ============================================

AIRLINES = load_json_data('airlines.json')
AIRPORTS = load_json_data('airports.json')
AIRLABS_API_KEY = load_api_key()

print(f"✅ Loaded {len(AIRLINES)} airlines, {len(AIRPORTS)} airports")

# ============================================
# ROUTES
# ============================================

@airport_bp.route('/')
def airport_menu():
    """Κύρια σελίδα μενού αεροδρομίου"""
    log_action("Προβολή μενού αεροδρομίου")
    return render_template('airport_menu.html')

@airport_bp.route('/arrivals')
def arrivals():
    """Σελίδα αφίξεων με live δεδομένα"""
    log_action("Προβολή σελίδας αφίξεων")
    try:
        response = requests.get(
            "http://airlabs.co/api/v9/schedules",
            params={'api_key': AIRLABS_API_KEY, 'arr_iata': 'ATH', 'limit': 100},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json().get('response', [])
            flights_list = []
            
            for f in data:
                try:
                    # Skip codeshares
                    if f.get('cs_airline_iata'):
                        continue
                    
                    # Ώρες
                    sched_raw = f.get('arr_time')
                    if not sched_raw:
                        continue
                    
                    s_str = str(sched_raw)
                    sched_time = s_str.split(' ')[1][:5] if ' ' in s_str else s_str
                    
                    est_raw = f.get('arr_estimated')
                    if est_raw:
                        e_str = str(est_raw)
                        est_time = e_str.split(' ')[1][:5] if ' ' in e_str else e_str
                    else:
                        est_time = sched_time
                    
                    is_delayed = (est_time != sched_time)
                    
                    # Lookups
                    al_code = f.get('airline_iata') or f.get('airline_icao') or 'UNK'
                    al_name = AIRLINES.get(al_code, al_code)
                    
                    dep_code = f.get('dep_iata') or f.get('dep_icao') or 'UNK'
                    dep_name = AIRPORTS.get(dep_code, dep_code)
                    
                    flights_list.append({
                        'sched_time': sched_time,
                        'est_time': est_time,
                        'is_delayed': is_delayed,
                        'flight_iata': f.get('flight_iata') or f.get('flight_number'),
                        'airline_iata': al_name,
                        'airline_code': al_code,
                        'dep_iata': dep_name,
                        'status': f.get('status'),
                        'aircraft': f.get('aircraft_icao') or ''
                    })
                except:
                    continue
            
            # Ταξινόμηση με χρονική λογική
            flights_list.sort(key=sort_flight_time)
            return render_template('arrivals.html', flights=flights_list)
        else:
            return render_template('arrivals.html', flights=[], error=f"API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Arrivals Error: {e}")
        return render_template('arrivals.html', flights=[], error="Data Error")

@airport_bp.route('/departures')
def departures():
    """Σελίδα αναχωρήσεων με live δεδομένα"""
    log_action("Προβολή σελίδας αναχωρήσεων")
    try:
        url = "http://airlabs.co/api/v9/schedules"
        params = {
            'api_key': AIRLABS_API_KEY,
            'dep_iata': 'ATH',
            'limit': 100
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json().get('response', [])
            flights_list = []
            
            for f in data:
                try:
                    # Skip codeshares
                    if f.get('cs_airline_iata'):
                        continue
                    
                    # Ώρες αναχώρησης
                    sched_raw = f.get('dep_time')
                    if not sched_raw:
                        continue
                    
                    s_str = str(sched_raw)
                    sched_time = s_str.split(' ')[1][:5] if ' ' in s_str else s_str
                    
                    est_raw = f.get('dep_estimated')
                    if est_raw:
                        e_str = str(est_raw)
                        est_time = e_str.split(' ')[1][:5] if ' ' in e_str else e_str
                    else:
                        est_time = sched_time
                    
                    is_delayed = (est_time != sched_time)
                    
                    # Lookups
                    al_code = f.get('airline_iata') or f.get('airline_icao') or 'UNK'
                    al_name = AIRLINES.get(al_code, al_code)
                    
                    arr_code = f.get('arr_iata') or f.get('arr_icao') or 'UNK'
                    arr_name = AIRPORTS.get(arr_code, arr_code)
                    
                    flights_list.append({
                        'sched_time': sched_time,
                        'est_time': est_time,
                        'is_delayed': is_delayed,
                        'flight_iata': f.get('flight_iata') or f.get('flight_number'),
                        'airline_iata': al_name,
                        'airline_code': al_code,
                        'arr_iata': arr_name,
                        'status': f.get('status'),
                        'aircraft': f.get('aircraft_icao') or ''
                    })
                except:
                    continue
            
            # Ταξινόμηση με χρονική λογική
            flights_list.sort(key=sort_flight_time)
            return render_template('departures.html', flights=flights_list)
        else:
            return render_template('departures.html', flights=[], error=f"API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Departures Error: {e}")
        return render_template('departures.html', flights=[], error="Data Error")


# ==================== AIRLINES ROUTES ====================

@airport_bp.route('/airlines')
def airlines():
    """Σελίδα διαχείρισης αεροπορικών εταιρειών"""
    log_action("Προβολή σελίδας αεροπορικών")
    
    # Παίρνουμε sorting parameters
    sort_by = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')
    
    # Validation
    valid_sorts = ['name', 'entrance']
    if sort_by not in valid_sorts:
        sort_by = 'name'
    
    if order not in ['asc', 'desc']:
        order = 'asc'
    
    # Φόρτωση από βάση
    conn = get_db_connection()
    
    # NULLS LAST για το entrance
    if sort_by == 'entrance':
        query = f"""
            SELECT * FROM airlines 
            ORDER BY 
                CASE WHEN entrance IS NULL THEN 1 ELSE 0 END,
                entrance {order.upper()},
                name ASC
        """
    else:
        query = f"SELECT * FROM airlines ORDER BY {sort_by} {order.upper()}"
    
    airlines_data = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('airlines.html', 
                         airlines=airlines_data,
                         sort_by=sort_by,
                         order=order)


@airport_bp.route('/airlines/add', methods=['POST'])
def add_airline():
    name = request.form.get('name', '').strip()
    entrance = request.form.get('entrance', '').strip()
    
    if not name:
        flash('Το όνομα είναι υποχρεωτικό!', 'error')
        return redirect(url_for('airport.airlines'))
    
    # Μετατροπή entrance σε None αν είναι κενό
    entrance_val = None if entrance == '' else int(entrance)
    
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO airlines (name, entrance) VALUES (?, ?)",
            (name, entrance_val)
        )
        conn.commit()
        conn.close()
        flash(f'Η αεροπορική "{name}" προστέθηκε επιτυχώς!', 'success')
    except sqlite3.IntegrityError:
        flash(f'Η αεροπορική "{name}" υπάρχει ήδη!', 'error')
    except Exception as e:
        flash(f'Σφάλμα: {str(e)}', 'error')
    
    return redirect(url_for('airport.airlines'))


@airport_bp.route('/airlines/edit/<int:airline_id>', methods=['GET', 'POST'])
def edit_airline(airline_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        entrance = request.form.get('entrance', '').strip()
        
        if not name:
            flash('Το όνομα είναι υποχρεωτικό!', 'error')
            return redirect(url_for('airport.edit_airline', airline_id=airline_id))
        
        entrance_val = None if entrance == '' else int(entrance)
        
        try:
            conn.execute(
                "UPDATE airlines SET name = ?, entrance = ? WHERE id = ?",
                (name, entrance_val, airline_id)
            )
            conn.commit()
            conn.close()
            flash(f'Η αεροπορική ενημερώθηκε επιτυχώς!', 'success')
            return redirect(url_for('airport.airlines'))
        except Exception as e:
            flash(f'Σφάλμα: {str(e)}', 'error')
            return redirect(url_for('airport.edit_airline', airline_id=airline_id))
    
    # GET request
    airline = conn.execute("SELECT * FROM airlines WHERE id = ?", (airline_id,)).fetchone()
    conn.close()
    
    if not airline:
        flash('Η αεροπορική δεν βρέθηκε!', 'error')
        return redirect(url_for('airport.airlines'))
    
    return render_template('edit_airline.html', airline=airline)


@airport_bp.route('/airlines/delete/<int:airline_id>', methods=['POST'])
def delete_airline(airline_id):
    try:
        conn = get_db_connection()
        airline = conn.execute("SELECT name FROM airlines WHERE id = ?", (airline_id,)).fetchone()
        
        if airline:
            conn.execute("DELETE FROM airlines WHERE id = ?", (airline_id,))
            conn.commit()
            flash(f'Η αεροπορική "{airline["name"]}" διαγράφηκε!', 'success')
        else:
            flash('Η αεροπορική δεν βρέθηκε!', 'error')
        
        conn.close()
    except Exception as e:
        flash(f'Σφάλμα: {str(e)}', 'error')
    
    return redirect(url_for('airport.airlines'))
