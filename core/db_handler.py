import sqlite3
import os
import pandas as pd
import time

# Define the database path relative to the project structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "data", "invoices.db")

def create_db():
    """Create the invoices database with all necessary tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (p
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            invoice_type TEXT,
            currency TEXT,
            buyer_name TEXT,
            buyer_legal_id TEXT,
            buyer_vat_id TEXT,
            buyer_street TEXT,
            buyer_city TEXT,
            buyer_county TEXT,
            buyer_postal_code TEXT,
            buyer_country TEXT,
            payment_terms TEXT,
            invoice_lines TEXT,
            total_no_vat REAL,
            total_vat REAL,
            total_payment REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        conn.close()

def insert_invoice(data: dict):
    """Insert a new invoice into the database with retry logic"""
    create_db()  # Ensure database exists
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Map Romanian column names to database column names
            column_mapping = {
                "Număr factură": "invoice_number",
                "Data emiterii": "issue_date",
                "Tip factură": "invoice_type",
                "Monedă": "currency",
                "Nume cumpărător": "buyer_name",
                "ID legal cumpărător": "buyer_legal_id",
                "ID TVA cumpărător": "buyer_vat_id",
                "Stradă cumpărător": "buyer_street",
                "Oraș cumpărător": "buyer_city",
                "Județ cumpărător": "buyer_county",
                "Cod poștal cumpărător": "buyer_postal_code",
                "Țară cumpărător": "buyer_country",
                "Termeni plată": "payment_terms",
                "Linii factură (produse)": "invoice_lines",
                "Valoare totală fără TVA": "total_no_vat",
                "Total TVA": "total_vat",
                "Total plată": "total_payment"
            }
            
            # Convert Romanian keys to English database keys
            mapped_data = {column_mapping.get(k, k): v for k, v in data.items()}
            
            # Ensure required fields are not None
            for key in ['invoice_number', 'issue_date']:
                if not mapped_data.get(key):
                    mapped_data[key] = ""
            
            columns = ', '.join(mapped_data.keys())
            placeholders = ', '.join('?' for _ in mapped_data)
            sql = f"INSERT INTO invoices ({columns}) VALUES ({placeholders})"
            c.execute(sql, tuple(mapped_data.values()))
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(1)  # Wait before retrying
                continue
            print(f"Error inserting invoice: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error inserting invoice: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()

def get_all_invoices():
    """Get all invoices from database as DataFrame with Romanian column names"""
    create_db()  # Ensure database exists
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Map database columns to Romanian names for UI consistency
        reverse_mapping = {
            "invoice_number": "Număr factură",
            "issue_date": "Data emiterii",
            "invoice_type": "Tip factură",
            "currency": "Monedă",
            "buyer_name": "Nume cumpărător",
            "buyer_legal_id": "ID legal cumpărător",
            "buyer_vat_id": "ID TVA cumpărător",
            "buyer_street": "Stradă cumpărător",
            "buyer_city": "Oraș cumpărător",
            "buyer_county": "Județ cumpărător",
            "buyer_postal_code": "Cod poștal cumpărător",
            "buyer_country": "Țară cumpărător",
            "payment_terms": "Termeni plată",
            "invoice_lines": "Linii factură (produse)",
            "total_no_vat": "Valoare totală fără TVA",
            "total_vat": "Total TVA",
            "total_payment": "Total plată"
        }
        
        df = pd.read_sql_query("SELECT * FROM invoices ORDER BY issue_date DESC", conn)
        conn.close()
        
        if df.empty:
            return None
            
        # Rename columns to Romanian for UI consistency
        df = df.rename(columns=reverse_mapping)
        
        # Drop internal columns that shouldn't be shown in UI
        columns_to_drop = ['id', 'created_at']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        return df
    except Exception as e:
        print(f"Error fetching invoices: {e}")
        if 'conn' in locals():
            conn.close()
        return None

def update_invoice(invoice_id: int, data: dict):
    """Update an existing invoice in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Map Romanian column names to database column names
        column_mapping = {
            "Număr factură": "invoice_number",
            "Data emiterii": "issue_date",
            "Tip factură": "invoice_type",
            "Monedă": "currency",
            "Nume cumpărător": "buyer_name",
            "ID legal cumpărător": "buyer_legal_id",
            "ID TVA cumpărător": "buyer_vat_id",
            "Stradă cumpărător": "buyer_street",
            "Oraș cumpărător": "buyer_city",
            "Județ cumpărător": "buyer_county",
            "Cod poștal cumpărător": "buyer_postal_code",
            "Țară cumpărător": "buyer_country",
            "Termeni plată": "payment_terms",
            "Linii factură (produse)": "invoice_lines",
            "Valoare totală fără TVA": "total_no_vat",
            "Total TVA": "total_vat",
            "Total plată": "total_payment"
        }
        
        mapped_data = {column_mapping.get(k, k): v for k, v in data.items()}
        set_clause = ', '.join(f"{col} = ?" for col in mapped_data.keys())
        sql = f"UPDATE invoices SET {set_clause} WHERE id = ?"
        c.execute(sql, tuple(mapped_data.values()) + (invoice_id,))
        conn.commit()
    except Exception as e:
        print(f"Error updating invoice: {e}")
        raise
    finally:
        conn.close()

def delete_invoice(invoice_id: int):
    """Delete an invoice from the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting invoice: {e}")
        raise
    finally:
        conn.close()

def get_invoice_stats():
    """Return detailed statistics for invoices with advanced analysis"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Total facturi
        c.execute("SELECT COUNT(*) FROM invoices")
        total_count = c.fetchone()[0]

        # Total fără TVA
        c.execute("SELECT SUM(total_no_vat) FROM invoices WHERE total_no_vat IS NOT NULL")
        total_without_vat = c.fetchone()[0] or 0

        # Total TVA
        c.execute("SELECT SUM(total_vat) FROM invoices WHERE total_vat IS NOT NULL")
        total_vat = c.fetchone()[0] or 0

        # Total cu TVA
        total_with_vat = total_without_vat + total_vat

        # Medii pe factură
        c.execute("SELECT AVG(total_no_vat), AVG(total_vat), AVG(total_payment) FROM invoices")
        avg_no_vat, avg_vat, avg_payment = c.fetchone()
        avg_no_vat = avg_no_vat or 0
        avg_vat = avg_vat or 0
        avg_payment = avg_payment or 0

        # Distribuția TVA
        c.execute("""
            SELECT AVG(CASE WHEN total_no_vat>0 THEN (total_vat/total_no_vat)*100 ELSE 0 END) FROM invoices
        """)
        avg_vat_percent = c.fetchone()[0] or 0

        c.execute("SELECT COUNT(*) FROM invoices WHERE total_vat IS NULL OR total_vat=0")
        pct_no_vat = (c.fetchone()[0] / total_count * 100) if total_count else 0

        # Grafic lunar stacked Net + TVA și valoare medie pe lună
        c.execute("""
            SELECT substr(issue_date,1,7) as month,
                   SUM(total_no_vat) as sum_no_vat,
                   SUM(total_vat) as sum_vat,
                   SUM(total_payment) as sum_with_vat,
                   COUNT(*) as count,
                   AVG(total_payment) as avg_payment
            FROM invoices
            WHERE issue_date IS NOT NULL
            GROUP BY substr(issue_date,1,7)
            ORDER BY month ASC
        """)
        monthly_rows = c.fetchall()
        monthly_data = [(m[0], m[1], m[2], m[3]) for m in monthly_rows]  # stacked bar
        monthly_count = [(m[0], m[4]) for m in monthly_rows]                # număr facturi
        monthly_avg = [(m[0], m[5]) for m in monthly_rows]                  # media facturilor

        # Creștere/scădere lunar (%) față de luna precedentă
        monthly_growth = []
        for i in range(1, len(monthly_rows)):
            prev = monthly_rows[i-1][3]
            curr = monthly_rows[i][3]
            growth = ((curr - prev) / prev * 100) if prev else 0
            monthly_growth.append((monthly_rows[i][0], growth))

        # Top 5 clienți după valoare totală
        c.execute("""
            SELECT buyer_name, SUM(total_payment) as total 
            FROM invoices
            GROUP BY buyer_name
            ORDER BY total DESC
            LIMIT 5
        """)
        top_clients = c.fetchall()

        return {
            'total_count': total_count,
            'total_without_vat': total_without_vat,
            'total_vat': total_vat,
            'total_with_vat': total_with_vat,
            'avg_no_vat': avg_no_vat,
            'avg_vat': avg_vat,
            'avg_payment': avg_payment,
            'avg_vat_percent': avg_vat_percent,
            'pct_no_vat': pct_no_vat,
            'monthly_data': monthly_data,
            'monthly_count': monthly_count,
            'monthly_avg': monthly_avg,
            'monthly_growth': monthly_growth,
            'top_clients': top_clients
        }

    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}
    finally:
        if 'conn' in locals():
            conn.close()



if __name__ == "__main__":
    create_db()
    print("Database created successfully!")