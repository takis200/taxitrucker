import sqlite3

conn = sqlite3.connect('taxi.db')
cursor = conn.cursor()

# 1. Διαγραφή όλων των διαδρομών
cursor.execute("DELETE FROM rides")
print("Διαγράφηκαν όλες οι διαδρομές.")

# 2. Διαγραφή ιστορικού credits (logs)
cursor.execute("DELETE FROM credit_check")
print("Διαγράφηκε το ιστορικό credits.")

# 3. Διαγραφή εσόδων εφαρμογών (apps)
cursor.execute("DELETE FROM app_earnings")
print("Διαγράφηκαν τα έσοδα εφαρμογών.")

# 4. Διαγραφή εξόδων (expenses)
cursor.execute("DELETE FROM expenses")
print("Διαγράφηκαν τα έξοδα.")

# Προσοχή: ΔΕΝ σβήνουμε τα hotels, destinations, drivers, rates, settings
conn.commit()
conn.close()
print("Η βάση καθαρίστηκε επιτυχώς!")
