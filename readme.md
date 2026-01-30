
# 🚕 Taxi Tracker

> Ολοκληρωμένο σύστημα διαχείρισης ταξί με παρακολούθηση διαδρομών, credits, service & πτήσεων αεροδρομίου

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Περιεχόμενα

- [Επισκόπηση](#-επισκόπηση)
- [Χαρακτηριστικά](#-χαρακτηριστικά)
- [Αρχιτεκτονική](#-αρχιτεκτονική)
- [Εγκατάσταση](#-εγκατάσταση)
- [Χρήση](#-χρήση)
- [Δομή Project](#-δομή-project)
- [Database Schema](#-database-schema)
- [API Integrations](#-api-integrations)
- [Contributing](#-contributing)

---

## 🎯 Επισκόπηση

Το **Taxi Tracker** είναι μια web εφαρμογή διαχείρισης επιχείρησης ταξί που παρέχει:

- 📊 Διαχείριση διαδρομών (rides) και εσόδων
- 💳 Σύστημα credits για ξενοδοχεία
- 🔧 Παρακολούθηση service & συντηρήσεων
- 👥 Διαχείριση οδηγών
- ✈️ Live πληροφορίες πτήσεων αεροδρομίου (arrivals/departures)
- 🏢 Διαχείριση αεροπορικών εταιρειών & εισόδων τερματικού
- 📈 Ιστορικό & αναφορές

---

## ✨ Χαρακτηριστικά

### 🚗 Διαχείριση Διαδρομών
- Καταγραφή διαδρομών με ξενοδοχείο, προορισμό, τιμή & διόδια
- Αυτόματος υπολογισμός credits
- Εξαγωγή σε Excel
- Ιστορικό με search & filters

### 💰 Credits System
- Έλεγχος ισορροπίας credits
- Προσθήκη/Αφαίρεση credits
- Διορθώσεις & σημειώσεις
- Tracking χρεών ανά πηγή

### 🔧 Service Management
- Καταγραφή συντηρήσεων με χιλιόμετρα
- Διαχείριση ανταλλακτικών (spare parts registry)
- Συνεργεία & τύποι service
- Υπολογισμός κόστους (εργασία + parts)

### 👥 Οδηγοί & Ξενοδοχεία
- Βάση δεδομένων οδηγών με τηλέφωνα
- Ξενοδοχεία με custom rates ανά προορισμό
- Import/Export από Excel
- Sorting & αναζήτηση

### ✈️ Airport Module
- **Live Arrivals Board** με API integration (AirLabs)
- **Live Departures Board**
- **Διαχείριση Airlines** με εισόδους τερματικού (1-4)
- Smart sorting (πτήσεις μεταμεσονύκτιες στο τέλος)
- Color-coded badges ανά είσοδο

### 📊 Εφαρμογές & Έξοδα
- Καταγραφή εσόδων από apps (FreeNow, Uber, Bolt)
- Παρακολούθηση καυσίμων & λοιπών εξόδων
- Ημερήσιες αναφορές

---

## 🏗️ Αρχιτεκτονική

### Tech Stack

Backend: Flask 3.1 (Python 3.13)
Database: SQLite 3
Frontend: HTML5, CSS3, Jinja2 Templates
UI: Material Icons, Roboto Font
JS: Sortable.js (drag & drop)
APIs: AirLabs API (flight data)

text

### Blueprint Structure

```python
routes/
├── main.py         # Αρχική σελίδα & index
├── drivers.py      # CRUD οδηγών
├── credits.py      # Credits management
├── history.py      # Ιστορικό διαδρομών
├── services.py     # Service & parts
├── settings.py     # Ξενοδοχεία, προορισμοί, rates
├── exportrates.py  # Export rates σε Excel
└── airport.py      # Arrivals, Departures, Airlines
🚀 Εγκατάσταση
Προαπαιτούμενα
Python 3.13+

pip

SQLite3

Βήματα
Clone το repository

bash
git clone https://github.com/takis200/taxitrucker.git
cd taxitrucker
Εγκατάσταση dependencies

bash
pip install flask requests pandas openpyxl
Δημιουργία βάσης δεδομένων

bash
# Χρήση του schema
sqlite3 taxi.db < taxi.db.sql

# Ή με το tool
python tools/schema_db.py
Προσθήκη API Key (για airport module)

bash
# Δημιούργησε αρχείο api/airlabs.env
echo "YOUR_AIRLABS_API_KEY" > api/airlabs.env
Λάβε δωρεάν API key από: https://airlabs.co

Import αρχικών δεδομένων

bash
# Οδηγοί
python tools/import_drivers_from_excel.py

# Rates
python tools/import_rates_from_excel.py

# Airlines
python tools/import_airlines.py
Εκκίνηση εφαρμογής

bash
python app.py
Άνοιγμα στον browser

text
http://localhost:5000
📚 Χρήση
Καταγραφή Διαδρομής
Πήγαινε στην Αρχική σελίδα

Επίλεξε Ξενοδοχείο & Προορισμό

Συμπλήρωσε Τιμή & Διόδια

Credits υπολογίζονται αυτόματα

Πάτα Καταχώρηση

Έλεγχος Credits
Πήγαινε στο Credits menu

Δες την τρέχουσα ισορροπία

Προσθήκη/Αφαίρεση credits με σημειώσεις

Tracking χρεών & πληρωμών

Live Πτήσεις
Πήγαινε στο Airport menu

Επίλεξε Αφίξεις ή Αναχωρήσεις

Δες live πτήσεις με:

Scheduled & Estimated time

Airline & προέλευση/προορισμός

Status & καθυστερήσεις

Διαχείριση Airlines
Airport → Αεροπορικές Εταιρείες

Προσθήκη νέας airline με είσοδο (1-4)

Αναζήτηση & sorting

Edit/Delete υπαρχουσών

📁 Δομή Project
text
taxitrucker/
├── api/
│   └── airlabs.env           # API key για AirLabs
├── data/
│   ├── airlines.json         # Lookup αεροπορικών (IATA codes)
│   ├── airlines.xlsx         # Import data για airlines
│   ├── airports.json         # Lookup αεροδρομίων (IATA codes)
│   ├── drivers.xlsx          # Import data οδηγών
│   ├── hotels.txt           # Λίστα ξενοδοχείων
│   ├── parts.xlsx           # Import ανταλλακτικών
│   └── rates.xlsx           # Import rates ξενοδοχείων
├── misc/
│   └── githubtree.txt       # Project structure
├── routes/
│   ├── __init__.py
│   ├── airport.py           # Airport routes (arrivals, departures, airlines)
│   ├── credits.py           # Credits management
│   ├── drivers.py           # Drivers CRUD
│   ├── exportrates.py       # Excel exports
│   ├── history.py           # Rides history
│   ├── main.py              # Main routes (index, ride entry)
│   ├── services.py          # Service & parts management
│   └── settings.py          # Hotels, destinations, rates
├── static/
│   ├── css/
│   │   └── style.css        # Global styles
│   ├── fonts/               # Roboto & Material Icons
│   ├── icons/               # Favicons
│   └── js/
│       └── Sortable.min.js  # Drag & drop library
├── templates/
│   ├── airlines.html        # Airlines management page
│   ├── airport_menu.html    # Airport main menu
│   ├── arrivals.html        # Live arrivals board
│   ├── base.html            # Base template (navigation)
│   ├── credits.html         # Credits page
│   ├── departures.html      # Live departures board
│   ├── drivers.html         # Drivers list & CRUD
│   ├── edit_airline.html    # Edit airline form
│   ├── edit_*.html          # Various edit forms
│   ├── history.html         # Rides history
│   ├── index.html           # Home page (ride entry)
│   ├── services.html        # Services list
│   ├── settings.html        # Hotels & destinations
│   └── workshops.html       # Workshops management
├── tools/
│   ├── import_airlines.py   # Import airlines από Excel/JSON
│   ├── import_drivers_from_excel.py
│   ├── import_rates_from_excel.py
│   ├── reset_db.py          # Reset database
│   └── schema_db.py         # Create database schema
├── app.py                   # Flask app entry point
├── inport.py                # Legacy import script
├── services_repo.py         # Services data access layer
├── taxi.db                  # SQLite database (generated)
├── taxi.db.sql              # Database schema SQL
└── utils.py                 # Utility functions (DB, logging, defaults)
🗄️ Database Schema
Κύριοι Πίνακες
airlines
sql
id INTEGER PRIMARY KEY
name TEXT UNIQUE NOT NULL
entrance INTEGER (1-4 or NULL)
rides
sql
id INTEGER PRIMARY KEY
date TEXT
hotel_name TEXT
dest_name TEXT
price REAL
tolls REAL
credits_charged REAL
drivers
sql
id INTEGER PRIMARY KEY
col_new TEXT
col_old TEXT
name TEXT NOT NULL
phone TEXT
credit_check
sql
id INTEGER PRIMARY KEY
date TEXT UNIQUE
start_balance INTEGER
end_balance INTEGER
added_credits INTEGER
correction INTEGER
debt_source TEXT
is_paid INTEGER (boolean)
notes TEXT
services
sql
id INTEGER PRIMARY KEY
service_date TEXT
odometer_km INTEGER
workshop_name TEXT
labor_cost REAL
note TEXT
created_at TEXT
service_lines
sql
id INTEGER PRIMARY KEY
service_id INTEGER (FK → services)
part_code TEXT
part_description TEXT
qty REAL
unit_price REAL
line_total REAL
hotels & destinations & rates
sql
hotels: id, name, sort_order, is_active
destinations: id, name, sort_order, is_active
rates: hotel_id (FK), dest_id (FK), credits
Indexes
idx_services_date on services(service_date)

idx_lines_service_id on service_lines(service_id)

ux_hotels_name UNIQUE on hotels(name)

🔌 API Integrations
AirLabs API
Endpoint: http://airlabs.co/api/v9/schedules

Used for:

Live arrivals (arr_iata=ATH)

Live departures (dep_iata=ATH)

Features:

Automatic filtering of codeshare flights

Time parsing & formatting

Delay detection

Airline & airport name lookup από JSON

Rate Limits: Free tier = 100 requests/day

🎨 UI/UX Features
Design System
Colors: Material Design palette

Typography: Roboto (Greek + Latin support)

Icons: Material Icons

Layout: Responsive grid system

Special Features
🔍 Live search σε πίνακες

↕️ Sorting με arrows

🎨 Color-coded badges (airlines entrances, delays)

📱 Mobile-optimized navigation

⏱️ Smart time sorting (μεταμεσονύκτιες πτήσεις στο τέλος)

🛠️ Development
Adding a New Route
Δημιούργησε αρχείο στο routes/your_module.py

python
from flask import Blueprint, render_template

your_bp = Blueprint('your_module', __name__)

@your_bp.route('/your-path')
def your_function():
    return render_template('your_template.html')
Register στο app.py

python
from routes.your_module import your_bp
app.register_blueprint(your_bp)
Δημιούργησε template στο templates/your_template.html

Database Migrations
bash
# Backup current DB
cp taxi.db taxi.db.backup

# Apply changes
sqlite3 taxi.db < your_migration.sql

# Or reset entirely
python tools/reset_db.py
Logging
Όλα τα actions καταγράφονται στο logs/activity_YYYY-MM.txt:

python
from utils import log_action
log_action("User performed action X")
📊 Import/Export
Import Airlines από Excel
bash
python tools/import_airlines.py
Excel format:

text
name                | entrance
--------------------|----------
Aegean Airlines     | 1
Ryanair            | 2
Wizz Air           | (empty for no entrance)
Export Rates σε Excel
Πήγαινε στο Settings menu

Πάτα Εξαγωγή Rates (Excel)

Κατέβασε rates_YYYY-MM-DD.xlsx

🤝 Contributing
Contributions are welcome! Please:

Fork το repo

Create feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open Pull Request

📝 License
MIT License - see LICENSE file for details

👨‍💻 Author
Takis - GitHub

🙏 Acknowledgments
Flask - Web framework

AirLabs - Flight data API

Material Icons - Icon set

SortableJS - Drag & drop

📞 Support
Για ερωτήσεις ή issues, άνοιξε ένα GitHub Issue

Made with ❤️ for taxi drivers in Greece 🇬🇷