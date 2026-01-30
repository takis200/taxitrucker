import sqlite3
import pandas as pd
import os

DB_NAME = "taxi.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# ΔΙΑΓΡΑΦΗ του παλιού πίνακα (αν υπάρχει)
print("🗑️  Διαγραφή παλιού πίνακα airlines (αν υπάρχει)...")
cursor.execute("DROP TABLE IF EXISTS airlines")
conn.commit()

# ΔΗΜΙΟΥΡΓΙΑ νέου πίνακα (entrance μπορεί να είναι NULL)
print("📋 Δημιουργία νέου πίνακα airlines...")
cursor.execute("""
CREATE TABLE airlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    entrance INTEGER CHECK(entrance IS NULL OR (entrance >= 1 AND entrance <= 4))
);
""")

conn.commit()
print("✅ Ο πίνακας δημιουργήθηκε επιτυχώς!\n")

# Εισαγωγή από Excel
excel_file = os.path.join('data', 'airlines.xlsx')

try:
    df = pd.read_excel(excel_file)
    
    print(f"📂 Βρέθηκαν {len(df)} γραμμές στο Excel\n")
    
    # ΕΛΕΓΧΟΣ ΓΙΑ ΔΙΠΛΟΤΥΠΑ ΟΝΟΜΑΤΑ
    print("🔍 Έλεγχος για διπλότυπα ονόματα...")
    duplicates = df[df.duplicated(subset=['name'], keep=False)]
    
    if not duplicates.empty:
        print("\n⚠️  ΒΡΕΘΗΚΑΝ ΔΙΠΛΟΤΥΠΑ ΟΝΟΜΑΤΑ:\n")
        duplicate_names = duplicates['name'].unique()
        for name in duplicate_names:
            rows = df[df['name'] == name]
            print(f"  ❌ '{name}' εμφανίζεται {len(rows)} φορές:")
            for idx, row in rows.iterrows():
                entrance_str = f"Είσοδος {int(row['entrance'])}" if pd.notna(row['entrance']) else "Χωρίς είσοδο"
                print(f"     - Γραμμή {idx+2}: {entrance_str}")
        
        print("\n💡 Διόρθωσε το Excel (διάγραψε ή μετονόμασε τα διπλότυπα) και ξανατρέξε το script!")
        conn.close()
        exit()
    
    print("✅ Δεν βρέθηκαν διπλότυπα!\n")
    
    # ΕΛΕΓΧΟΣ ΕΙΣΟΔΟΥ (1-4)
    print("🔍 Έλεγχος τιμών εισόδου...")
    errors = []
    
    for index, row in df.iterrows():
        # Αν η είσοδος είναι κενή, είναι OK
        if pd.isna(row['entrance']):
            continue
        
        try:
            entrance_val = int(row['entrance'])
            
            # Αν δεν είναι κενή, πρέπει να είναι 1-4
            if entrance_val < 1 or entrance_val > 4:
                errors.append(f"  ❌ Γραμμή {index+2}: '{row['name']}' - Είσοδος {entrance_val} (πρέπει 1-4 ή κενό)")
        except:
            errors.append(f"  ❌ Γραμμή {index+2}: '{row['name']}' - Η είσοδος δεν είναι αριθμός")
    
    if errors:
        print("\n⚠️  ΠΡΟΒΛΗΜΑΤΑ ΣΤΟ EXCEL:\n")
        for err in errors:
            print(err)
        print("\n💡 Διόρθωσε το Excel και ξανατρέξε το script!")
        conn.close()
        exit()
    
    print("✅ Όλες οι τιμές εισόδου είναι έγκυρες!\n")
    
    # ΕΙΣΑΓΩΓΗ ΔΕΔΟΜΕΝΩΝ
    print("📥 Εισαγωγή δεδομένων...\n")
    count = 0
    no_entrance_count = 0
    
    for index, row in df.iterrows():
        # Μετατροπή entrance (None αν είναι κενό)
        entrance_val = None if pd.isna(row['entrance']) else int(row['entrance'])
        
        # Προσθήκη νέας
        cursor.execute(
            "INSERT INTO airlines (name, entrance) VALUES (?, ?)",
            (row['name'], entrance_val)
        )
        count += 1
        
        if entrance_val:
            print(f"➕ {row['name']} → Είσοδος {entrance_val}")
        else:
            print(f"➕ {row['name']} → ⏳ Χωρίς είσοδο")
            no_entrance_count += 1
    
    conn.commit()
    
    print(f"\n✅ Ολοκληρώθηκε!")
    print(f"   📥 Συνολικές εγγραφές: {count}")
    print(f"   🚪 Με είσοδο: {count - no_entrance_count}")
    print(f"   ⏳ Χωρίς είσοδο: {no_entrance_count}")
    
    # Εμφάνιση ανά είσοδο
    print(f"\n📊 Κατανομή ανά είσοδο:")
    for i in range(1, 5):
        cnt = cursor.execute("SELECT COUNT(*) FROM airlines WHERE entrance = ?", (i,)).fetchone()[0]
        if cnt > 0:
            print(f"   Είσοδος {i}: {cnt} αεροπορικές")
    
    no_ent = cursor.execute("SELECT COUNT(*) FROM airlines WHERE entrance IS NULL").fetchone()[0]
    if no_ent > 0:
        print(f"   Χωρίς είσοδο: {no_ent} αεροπορικές")
    
except FileNotFoundError:
    print(f"❌ Το αρχείο {excel_file} δεν βρέθηκε!")
    print(f"💡 Βεβαιώσου ότι υπάρχει το αρχείο: {os.path.abspath(excel_file)}")
except KeyError as e:
    print(f"❌ Λείπει στήλη στο Excel: {e}")
    print("💡 Το Excel πρέπει να έχει στήλες: 'name' και 'entrance'")
except Exception as e:
    print(f"❌ Σφάλμα: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()

print("\n🎉 Τέλος!")
