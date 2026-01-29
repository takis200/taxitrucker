from flask import Blueprint, render_template
import requests
import json
import os

airport_bp = Blueprint('airport', __name__)

# --- ΣΥΝΑΡΤΗΣΗ ΦΟΡΤΩΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
def load_json_data(filename):
    try:
        # Βρίσκουμε το absolute path για να μην χάνεται το αρχείο
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {filename}: {e}")
        return {} # Επιστρέφουμε κενό λεξικό αν αποτύχει
    
# Φόρτωση των αρχείων ΜΙΑ φορά στην αρχή
AIRLINES = load_json_data('airlines.json')
AIRPORTS = load_json_data('airports.json')
    
# --- ΣΥΝΑΡΤΗΣΗ ΓΙΑ ΦΟΡΤΩΣΗ ΚΛΕΙΔΙΟΥ ---
def load_api_key():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # ΑΛΛΑΓΗ ΕΔΩ: Βάζουμε το σωστό όνομα αρχείου 'airlab.env'
        key_path = os.path.join(base_dir, 'api', 'airlabs.env') 
        
        with open(key_path, 'r') as f:
            # Το .strip() καθαρίζει κενά και αόρατους χαρακτήρες αλλαγής γραμμής
            return f.read().strip()
    except Exception as e:
        print(f"CRITICAL: Could not load API key from {key_path}: {e}")
        return None
    
AIRLABS_API_KEY = load_api_key()



@airport_bp.route('/arrivals')
def arrivals_board():
    try:
        url = "http://airlabs.co/api/v9/schedules"
        params = {
            'api_key': AIRLABS_API_KEY,
            'arr_iata': 'ATH',
            'limit': 50
        }
        
        response = requests.get(url, params=params, timeout=30) # No verify needed for http
        
        if response.status_code == 200:
            data = response.json().get('response', [])
            flights_list = []
            
            for f in data:
                try: # Ασφάλεια μέσα στο loop
                    # 1. Skip Codeshares
                    if f.get('cs_airline_iata'): continue

                    # 2. Ώρες
                    sched_raw = f.get('arr_time')
                    if not sched_raw: continue
                    
                    s_str = str(sched_raw)
                    sched_time = s_str.split(' ')[1][:5] if ' ' in s_str else s_str

                    est_raw = f.get('arr_estimated')
                    if est_raw:
                        e_str = str(est_raw)
                        est_time = e_str.split(' ')[1][:5] if ' ' in e_str else e_str
                    else:
                        est_time = sched_time

                    is_delayed = (est_time != sched_time)

                    # 3. Lookups από τα JSON αρχεία
                    # Αεροπορική
                    al_code = f.get('airline_iata') or f.get('airline_icao') or 'UNK'
                    # Ψάχνουμε στο φορτωμένο JSON, αλλιώς επιστρέφουμε τον κωδικό
                    al_name = AIRLINES.get(al_code, al_code)

                    # Προορισμός
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

                except Exception as loop_err:
                    print(f"Skipped row: {loop_err}")
                    continue

            flights_list.sort(key=lambda x: x['est_time'])
            return render_template('arrivals.html', flights=flights_list)
        
        else:
            return render_template('arrivals.html', flights=[], error=f"API Error: {response.status_code}")

    except Exception as e:
        print(f"Main Error: {e}")
        return render_template('arrivals.html', flights=[], error="Data Error")
