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
        CREATE TABLE IF NOT EXISTS invoices (
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
    """Get statistics about invoices in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Total count
        c.execute("SELECT COUNT(*) FROM invoices")
        total_count = c.fetchone()[0]
        
        # Total amount
        c.execute("SELECT SUM(total_payment) FROM invoices WHERE total_payment IS NOT NULL")
        result = c.fetchone()[0]
        total_amount = result if result else 0
        
        # Monthly breakdown
        c.execute("""
            SELECT substr(issue_date, 1, 7) as month, 
                   COUNT(*) as count, 
                   SUM(total_payment) as amount
            FROM invoices 
            WHERE issue_date IS NOT NULL 
            GROUP BY substr(issue_date, 1, 7)
            ORDER BY month DESC
            LIMIT 12
        """)
        monthly_data = c.fetchall()
        
        return {
            'total_count': total_count,
            'total_amount': total_amount,
            'monthly_data': monthly_data
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {'total_count': 0, 'total_amount': 0, 'monthly_data': []}
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_db()
    print("Database created successfully!")