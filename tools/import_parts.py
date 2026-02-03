import pandas as pd
import sqlite3
import os

# --- ΡΥΘΜΙΣΕΙΣ ---
EXCEL_FILE = "data/parts.xlsx"
DB_FILE = "taxi.db"

def import_simple_excel():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Το αρχείο '{EXCEL_FILE}' δεν βρέθηκε!")
        return

    print(f"📖 Ανάγνωση του {EXCEL_FILE}...")
    
    try:
        # Διαβάζουμε το Excel χωρίς να μας νοιάζουν τα ονόματα των στηλών
        # header=0 σημαίνει ότι η πρώτη γραμμή είναι τίτλοι (και τους αγνοούμε μετά)
        df = pd.read_excel(EXCEL_FILE, header=0)

        # Επιλέγουμε αυστηρά την 1η και 2η στήλη
        # iloc[:, 0] -> Όλες οι γραμμές, 1η στήλη
        # iloc[:, 1] -> Όλες οι γραμμές, 2η στήλη
        if df.shape[1] < 2:
            print("❌ Το αρχείο Excel πρέπει να έχει τουλάχιστον 2 στήλες!")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        count = 0
        skipped = 0

        print("🚀 Ξεκινάει η εισαγωγή...")

        for index, row in df.iterrows():
            # Καθαρισμός δεδομένων (strip αφαιρεί κενά στην αρχή/τέλος)
            p_code = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            p_desc = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""

            # Απαραίτητο να υπάρχει περιγραφή
            if not p_desc or p_desc.lower() == 'nan':
                print(f"⚠️ Γραμμή {index+2}: Παραλείφθηκε (κενή περιγραφή)")
                skipped += 1
                continue

            # Εισαγωγή
            try:
                cursor.execute(
                    "INSERT INTO spare_parts (code, description, notes) VALUES (?, ?, ?)",
                    (p_code, p_desc, "")
                )
                count += 1
            except Exception as e:
                print(f"⚠️ Σφάλμα στη γραμμή {index+2}: {e}")

        conn.commit()
        conn.close()
        
        print("-" * 30)
        print(f"✅ Ολοκληρώθηκε!")
        print(f"📥 Εισήχθησαν: {count}")
        print(f"⏩ Παραλείφθηκαν: {skipped}")

    except Exception as e:
        print(f"❌ Γενικό Σφάλμα: {e}")

if __name__ == "__main__":
    import_simple_excel()
