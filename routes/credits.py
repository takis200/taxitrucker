# --- 18. Διαχείριση Credits ---
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
# Υποθέτουμε ότι μετακινήσατε αυτές τις συναρτήσεις στο utils.py
from utils import get_db_connection, get_setting, log_action 

# Δημιουργία του Blueprint
credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/credits', methods=['GET', 'POST'])
def credits_check():
    conn = get_db_connection()
    
    # 1. Διαχείριση Ημερομηνιών
    today = datetime.now()
    selected_date_str = request.args.get('date', today.strftime('%Y-%m-%d'))
    
    # Επιλογή Μήνα για τον πίνακα ιστορικού (default: τρέχων μήνας)
    selected_month_str = request.args.get('month', selected_date_str[:7]) # 'YYYY-MM'
    
    # ΝΕΟ: Διαγραφή Log
    if request.method == 'POST' and 'delete_log' in request.form:
        date_val = request.form.get('date')
        conn.execute('DELETE FROM credit_check WHERE date = ?', (date_val,))
        conn.commit()
        flash('Η καταγραφή διαγράφηκε!')
        return redirect(url_for('credits.credits_check', date=date_val, month=date_val[:7]))    
    
    # 2. Αποθήκευση (POST) - ΙΔΙΟ ΜΕ ΠΡΙΝ
    if request.method == 'POST' and 'save_log' in request.form:
        date_val = request.form.get('date')
        start = int(request.form.get('start_balance') or 0)
        end = int(request.form.get('end_balance') or 0)
        added = int(request.form.get('added_credits') or 0)
        correction = int(request.form.get('correction') or 0)
        debt_source = request.form.get('debt_source', '')
        is_paid = 1 if request.form.get('is_paid') else 0
        if added == 0: is_paid = 1; debt_source = ''

        conn.execute('''
            INSERT OR REPLACE INTO credit_check 
            (date, start_balance, end_balance, added_credits, correction, debt_source, is_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (date_val, start, end, added, correction, debt_source, is_paid))
        conn.commit()
        flash('Αποθηκεύτηκε!')
        return redirect(url_for('credits.credits_check', date=date_val, month=date_val[:7]))

    if request.method == 'POST' and 'pay_debt' in request.form:
        log_id = request.form.get('log_id')
        conn.execute('UPDATE credit_check SET is_paid=1 WHERE id=?', (log_id,))
        conn.commit()
        flash('Εξοφλήθηκε!')
        return redirect(url_for('credits.credits_check', date=selected_date_str, month=selected_month_str))

    # 3. Δεδομένα για την πάνω κάρτα (Ημέρα)
    rides_credits = conn.execute('SELECT SUM(credits_charged) as total FROM rides WHERE date = ?', (selected_date_str,)).fetchone()['total'] or 0
    log = conn.execute('SELECT * FROM credit_check WHERE date = ?', (selected_date_str,)).fetchone()
    diff = 0
    if log:
        theoretical = (log['start_balance'] + log['added_credits'] + log['correction']) - log['end_balance']
        diff = rides_credits - theoretical

    # 4. Δεδομένα για τον Κάτω Πίνακα (Μήνας)
    # Φέρνουμε όλες τις εγγραφές του μήνα
    month_logs = conn.execute('''
        SELECT * FROM credit_check 
        WHERE strftime('%Y-%m', date) = ? 
        ORDER BY date DESC
    ''', (selected_month_str,)).fetchall()

    # Για κάθε μέρα του μήνα, πρέπει να υπολογίσουμε τη διαφορά
    history_data = []
    total_month_diff = 0
    
    for row in month_logs:
        day_rides = conn.execute('SELECT SUM(credits_charged) as total FROM rides WHERE date = ?', (row['date'],)).fetchone()['total'] or 0
        theo = (row['start_balance'] + row['added_credits'] + row['correction']) - row['end_balance']
        day_diff = day_rides - theo
        total_month_diff += day_diff
        
        history_data.append({
            'date': row['date'],
            'start': row['start_balance'],
            'end': row['end_balance'],
            'added': row['added_credits'],
            'correction': row['correction'],
            'diff': day_diff
        })

    # Εκκρεμείς Οφειλές
    debts = conn.execute('''
        SELECT * FROM credit_check 
        WHERE added_credits > 0 
        AND (strftime('%Y-%m', date) = ? OR is_paid = 0)
        ORDER BY date DESC
    ''', (selected_month_str,)).fetchall()
    conn.close()

    return render_template('credits.html', 
                           date=selected_date_str, 
                           rides_credits=rides_credits, 
                           log=log, diff=diff, debts=debts,
                           history=history_data,
                           selected_month=selected_month_str,
                           total_month_diff=total_month_diff)