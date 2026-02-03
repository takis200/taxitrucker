# --- 18. Διαχείριση Credits ---
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from utils import get_db_connection, get_setting, log_action 

credits_bp = Blueprint('credits', __name__)

@credits_bp.route('/credits', methods=['GET', 'POST'])
def credits_check():
    conn = get_db_connection()
    
    # 1. Διαχείριση Ημερομηνιών
    today = datetime.now()
    selected_date_str = request.args.get('date', today.strftime('%Y-%m-%d'))
    selected_month_str = request.args.get('month', selected_date_str[:7])
    
    # ΝΕΟ: Διαγραφή Log
    if request.method == 'POST' and 'delete_log' in request.form:
        date_val = request.form.get('date')
        conn.execute('DELETE FROM credit_check WHERE date = ?', (date_val,))
        conn.commit()
        flash('Η καταγραφή διαγράφηκε!')
        return redirect(url_for('credits.credits_check', date=date_val, month=date_val[:7]))    
    
    # 2. Αποθήκευση (POST)
    if request.method == 'POST' and 'save_log' in request.form:
        date_val = request.form.get('date')
        start = int(request.form.get('start_balance') or 0)
        end = int(request.form.get('end_balance') or 0)
        added = int(request.form.get('added_credits') or 0)
        correction = int(request.form.get('correction') or 0)
        debt_source = request.form.get('debt_source', '')
        is_paid = 1 if request.form.get('is_paid') else 0
        paid_date = today.strftime('%Y-%m-%d') if is_paid and added > 0 else None
        
        if added == 0: 
            is_paid = 1
            debt_source = ''
            paid_date = None

        # Έλεγχος αν υπάρχει ήδη εγγραφή
        existing = conn.execute('SELECT id, added_credits, is_paid FROM credit_check WHERE date = ?', (date_val,)).fetchone()
        
        conn.execute('''
            INSERT OR REPLACE INTO credit_check 
            (date, start_balance, end_balance, added_credits, correction, debt_source, is_paid, paid_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date_val, start, end, added, correction, debt_source, is_paid, paid_date))
        
        # Καταγραφή στο ιστορικό συναλλαγών (αν υπάρχει ο πίνακας)
        if added > 0 and not existing:
            last_id = conn.execute('SELECT last_insert_rowid() as id').fetchone()['id']
            conn.execute('''
                INSERT INTO credit_transactions 
                (credit_check_id, transaction_type, transaction_date, amount, debt_source)
                VALUES (?, 'purchase', ?, ?, ?)
            ''', (last_id, date_val, added, debt_source))
        
        conn.commit()
        flash('Αποθηκεύτηκε!')
        return redirect(url_for('credits.credits_check', date=date_val, month=date_val[:7]))

    # 3. ΕΝΗΜΕΡΩΣΗ: Εξόφληση με καταγραφή ημερομηνίας
    if request.method == 'POST' and 'pay_debt' in request.form:
        log_id = request.form.get('log_id')
        payment_date = today.strftime('%Y-%m-%d')
        
        # Ενημέρωση του credit_check
        conn.execute('''
            UPDATE credit_check 
            SET is_paid=1, paid_date=? 
            WHERE id=?
        ''', (payment_date, log_id))
        
        # Καταγραφή της πληρωμής στο ιστορικό
        debt_info = conn.execute('''
            SELECT added_credits, debt_source 
            FROM credit_check 
            WHERE id=?
        ''', (log_id,)).fetchone()
        
        if debt_info:
            conn.execute('''
                INSERT INTO credit_transactions 
                (credit_check_id, transaction_type, transaction_date, amount, debt_source)
                VALUES (?, 'payment', ?, ?, ?)
            ''', (log_id, payment_date, debt_info['added_credits'], debt_info['debt_source']))
        
        conn.commit()
        flash('Εξοφλήθηκε!')
        return redirect(url_for('credits.credits_check', date=selected_date_str, month=selected_month_str))

    # 4. Δεδομένα για την πάνω κάρτα (Ημέρα)
    rides_credits = conn.execute('SELECT SUM(credits_charged) as total FROM rides WHERE date = ?', (selected_date_str,)).fetchone()['total'] or 0
    log = conn.execute('SELECT * FROM credit_check WHERE date = ?', (selected_date_str,)).fetchone()
    diff = 0
    if log:
        theoretical = (log['start_balance'] + log['added_credits'] + log['correction']) - log['end_balance']
        diff = rides_credits - theoretical

    # 5. Δεδομένα για τον Κάτω Πίνακα (Μήνας)
    month_logs = conn.execute('''
        SELECT * FROM credit_check 
        WHERE strftime('%Y-%m', date) = ? 
        ORDER BY date DESC
    ''', (selected_month_str,)).fetchall()

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

    # 6. Εκκρεμείς Οφειλές
    debts = conn.execute('''
        SELECT * FROM credit_check 
        WHERE added_credits > 0 
        AND (strftime('%Y-%m', date) = ? OR is_paid = 0)
        ORDER BY date DESC
    ''', (selected_month_str,)).fetchall()
    
    # 7. ΝΕΟ: Πλήρες ιστορικό συναλλαγών για αναζήτηση
    transactions_history = conn.execute('''
        SELECT 
            t.*,
            c.date as original_date
        FROM credit_transactions t
        LEFT JOIN credit_check c ON t.credit_check_id = c.id
        ORDER BY t.transaction_date DESC
        LIMIT 50
    ''', ()).fetchall()
    
    conn.close()

    return render_template('credits.html', 
                           date=selected_date_str, 
                           rides_credits=rides_credits, 
                           log=log, diff=diff, debts=debts,
                           history=history_data,
                           selected_month=selected_month_str,
                           total_month_diff=total_month_diff,
                           transactions=transactions_history)

# ΝΕΟ: Route για αναζήτηση ιστορικού (ενημερωμένο)
@credits_bp.route('/credits/history')
def credits_history():
    conn = get_db_connection()
    
    # Φίλτρα αναζήτησης (μόνο ημερομηνία)
    search_date = request.args.get('date', '')
    
    query = '''
        SELECT 
            t.*,
            c.date as original_date,
            c.debt_source
        FROM credit_transactions t
        LEFT JOIN credit_check c ON t.credit_check_id = c.id
        WHERE 1=1
    '''
    params = []
    
    if search_date:
        query += ' AND t.transaction_date = ?'
        params.append(search_date)
    
    query += ' ORDER BY t.transaction_date DESC, t.id DESC LIMIT 100'
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('credits_history.html', transactions=transactions)


# ΝΕΟ: Διαγραφή συναλλαγής
@credits_bp.route('/credits/transaction/<int:id>/delete', methods=['POST'])
def delete_transaction(id):
    conn = get_db_connection()
    
    # Διαγραφή της συναλλαγής
    conn.execute('DELETE FROM credit_transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Η συναλλαγή διαγράφηκε!')
    return redirect(url_for('credits.credits_history'))


# ΝΕΟ: Σελίδα επεξεργασίας συναλλαγής
@credits_bp.route('/credits/transaction/<int:id>/edit', methods=['GET', 'POST'])
def edit_transaction(id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        transaction_date = request.form.get('transaction_date')
        amount = int(request.form.get('amount') or 0)
        notes = request.form.get('notes', '')
        
        conn.execute('''
            UPDATE credit_transactions 
            SET transaction_date = ?, amount = ?, notes = ?
            WHERE id = ?
        ''', (transaction_date, amount, notes, id))
        conn.commit()
        conn.close()
        
        flash('Η συναλλαγή ενημερώθηκε!')
        return redirect(url_for('credits.credits_history'))
    
    # GET: Φόρτωση δεδομένων
    transaction = conn.execute('''
        SELECT t.*, c.debt_source, c.date as original_date
        FROM credit_transactions t
        LEFT JOIN credit_check c ON t.credit_check_id = c.id
        WHERE t.id = ?
    ''', (id,)).fetchone()
    
    conn.close()
    
    if not transaction:
        flash('Η συναλλαγή δεν βρέθηκε!')
        return redirect(url_for('credits.credits_history'))
    
    return render_template('edit_transaction.html', transaction=transaction)
