# --- 19. Διαχείριση Services ---
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action 
import sys
import os

# Προσθήκη του parent directory για να βρει το services_repo.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services_repo  # <--- ΑΥΤΟ ΕΛΕΙΠΕ
# Δημιουργία του Blueprint
services_bp = Blueprint('services', __name__)

# --- 19. Διαχείριση Services ---
@services_bp.route('/services')
def services_list():
    services = services_repo.get_all_services()
    parts = services_repo.get_parts_history()
    return render_template('services.html', services=services, parts=parts)

@services_bp.route('/services/add', methods=['GET', 'POST'])
@services_bp.route('/services/add', methods=['GET', 'POST'])
def service_add():
    if request.method == 'POST':
        # --- ΚΩΔΙΚΑΣ ΑΠΟΘΗΚΕΥΣΗΣ (POST) ---
        data = {
            'date': request.form['service_date'],
            'km': request.form['odometer_km'],
            'workshop': request.form['workshop_name'],
            'labor': float(request.form['labor_cost'] or 0),
            'note': request.form['note']
        }
        
        codes = request.form.getlist('part_code[]')
        descs = request.form.getlist('part_description[]')
        qtys = request.form.getlist('qty[]')
        prices = request.form.getlist('unit_price[]')
        
        lines = []
        for i in range(len(descs)):
            if descs[i].strip():
                lines.append({
                    'code': codes[i],
                    'desc': descs[i],
                    'qty': float(qtys[i] or 1),
                    'price': float(prices[i] or 0)
                })
        
        services_repo.create_service(data, lines)
        return redirect(url_for('services.services_list'))
    
    # --- ΚΩΔΙΚΑΣ ΕΜΦΑΝΙΣΗΣ ΦΟΡΜΑΣ (GET) ---
    # Αυτό τρέχει ΜΟΝΟ αν δεν είναι POST (δηλαδή όταν ανοίγεις τη σελίδα)
    workshops = services_repo.get_all_workshops()
    parts_list = services_repo.get_all_parts_registry()
    
    return render_template('service_form.html', service=None, lines=[], workshops=workshops, parts_list=parts_list)

@services_bp.route('/services/edit/<int:id>', methods=['GET', 'POST'])
def service_edit(id):
    if request.method == 'POST':
        # Ίδια λογική με το Add, αλλά καλεί update
        data = {
            'date': request.form['service_date'],
            'km': request.form['odometer_km'],
            'workshop': request.form['workshop_name'],
            'labor': float(request.form['labor_cost'] or 0),
            'note': request.form['note']
        }
        
        codes = request.form.getlist('part_code[]')
        descs = request.form.getlist('part_description[]')
        qtys = request.form.getlist('qty[]')
        prices = request.form.getlist('unit_price[]')
        
        lines = []
        for i in range(len(descs)):
            if descs[i].strip():
                lines.append({
                    'code': codes[i],
                    'desc': descs[i],
                    'qty': float(qtys[i] or 1),
                    'price': float(prices[i] or 0)
                })
                
        services_repo.update_service(id, data, lines)
        return redirect(url_for('services.services_list'))

    # GET request: Φόρτωσε τα δεδομένα
    service, lines = services_repo.get_service_by_id(id)
    workshops = services_repo.get_all_workshops()
    parts_list = services_repo.get_all_parts_registry()
    return render_template('service_form.html', service=service, lines=lines, workshops=workshops, parts_list=parts_list)


@services_bp.route('/services/delete/<int:id>')
def service_delete(id):
    services_repo.delete_service(id)
    return redirect(url_for('services.services_list'))

# --- ROUTES ΓΙΑ ΣΥΝΕΡΓΕΙΑ ---
@services_bp.route('/workshops')
def workshops_list():
    workshops = services_repo.get_all_workshops()
    return render_template('workshops.html', workshops=workshops)

@services_bp.route('/workshop-types', methods=['GET', 'POST'])
def workshop_types_manage():
    if request.method == 'POST':
        new_type = request.form.get('name')
        if new_type:
            services_repo.create_workshop_type(new_type)
        return redirect(url_for('services.workshop_types_manage'))
    
    types = services_repo.get_all_workshop_types()
    return render_template('workshop_types.html', types=types)

@services_bp.route('/workshops/add', methods=['GET', 'POST'])
def workshop_add():
    if request.method == 'POST':
        services_repo.create_workshop(request.form)
        return redirect(url_for('services.workshops_list'))
    
    # Φέρνουμε τα είδη για να τα βάλουμε στο Select
    types = services_repo.get_all_workshop_types()
    return render_template('workshop_form.html', workshop=None, types=types)

@services_bp.route('/workshops/edit/<int:id>', methods=['GET', 'POST'])
def workshop_edit(id):
    if request.method == 'POST':
        services_repo.update_workshop(id, request.form)
        return redirect(url_for('services.workshops_list'))
    
    workshop = services_repo.get_workshop_by_id(id)
    types = services_repo.get_all_workshop_types() # <--- ΤΟ ΣΤΕΛΝΟΥΜΕ ΚΙ ΕΔΩ
    return render_template('workshop_form.html', workshop=workshop, types=types)

@services_bp.route('/workshops/delete/<int:id>')
def workshop_delete(id):
    services_repo.delete_workshop(id)
    return redirect(url_for('services.workshops_list'))

# --- ROUTES ΓΙΑ ΑΝΤΑΛΛΑΚΤΙΚΑ ---
@services_bp.route('/parts-registry')
def parts_registry_list():
    parts = services_repo.get_all_parts_registry()
    return render_template('parts_registry.html', parts=parts)

@services_bp.route('/parts-registry/add', methods=['GET', 'POST'])
def part_registry_add():
    if request.method == 'POST':
        services_repo.create_part_registry(request.form)
        return redirect(url_for('services.parts_registry_list'))
    return render_template('part_registry_form.html', part=None)

@services_bp.route('/parts-registry/edit/<int:id>', methods=['GET', 'POST'])
def part_registry_edit(id):
    if request.method == 'POST':
        services_repo.update_part_registry(id, request.form)
        return redirect(url_for('services.parts_registry_list'))
    part = services_repo.get_part_registry_by_id(id)
    return render_template('part_registry_form.html', part=part)

@services_bp.route('/parts-registry/delete/<int:id>')
def part_registry_delete(id):
    services_repo.delete_part_registry(id)
    return redirect(url_for('services.parts_registry_list'))

@services_bp.route('/workshop-types/edit/<int:id>', methods=['POST'])
def workshop_type_edit(id):
    new_name = request.form.get('name')
    if new_name:
        services_repo.update_workshop_type(id, new_name)
    return redirect(url_for('services.workshop_types_manage'))

@services_bp.route('/workshop-types/delete/<int:id>')
def workshop_type_delete(id):
    services_repo.delete_workshop_type(id)
    return redirect(url_for('services.workshop_types_manage'))
