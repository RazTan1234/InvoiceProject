import random
import datetime
import sys, os

# adaugăm corect calea ca să meargă importul chiar dacă rulăm din scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import db_handler

def clear_database():
    """Șterge toate facturile existente din baza de date"""
    import sqlite3
    conn = sqlite3.connect(db_handler.DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM invoices")
    conn.commit()
    conn.close()
    print("⚠️  Toate facturile existente au fost șterse.")

def generate_random_invoice(n):
    return {
        "Număr factură": f"INV{1000+n}",
        "Data emiterii": (datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))).isoformat(),
        "Tip factură": random.choice(["Factura", "Proformă"]),
        "Monedă": random.choice(["RON", "EUR", "USD"]),
        "Nume cumpărător": random.choice(["Client SRL", "Firma X", "Compania Y", "Partener Z"]),
        "ID legal cumpărător": f"J{random.randint(100,999)}/2025",
        "ID TVA cumpărător": f"RO{random.randint(100000,999999)}",
        "Stradă cumpărător": random.choice(["Str. Libertății 10", "Bd. Unirii 5", "Calea Victoriei 20"]),
        "Oraș cumpărător": random.choice(["București", "Cluj", "Timișoara", "Iași"]),
        "Județ cumpărător": random.choice(["Ilfov", "Cluj", "Timiș", "Iași"]),
        "Cod poștal cumpărător": str(random.randint(100000, 999999)),
        "Țară cumpărător": "România",
        "Termeni plată": random.choice(["15 zile", "30 zile", "60 zile"]),
        "Linii factură (produse)": "; ".join([
            f"Produs{j} x{random.randint(1,5)} @ {random.randint(50,500)} RON"
            for j in range(random.randint(1, 5))
        ]),
        "Valoare totală fără TVA": round(random.uniform(500, 5000), 2),
        "Total TVA": round(random.uniform(100, 1000), 2),
        "Total plată": 0.0  # calculăm după
    }

def populate_db(num_invoices=100):
    clear_database()
    for i in range(num_invoices):
        invoice = generate_random_invoice(i)
        invoice["Total plată"] = round(invoice["Valoare totală fără TVA"] + invoice["Total TVA"], 2)
        db_handler.insert_invoice(invoice)
    print(f"✅ {num_invoices} facturi generate și salvate în baza de date.")

if __name__ == "__main__":
    populate_db(100)
