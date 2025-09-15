import pandas as pd
import os

# BASE_DIR = directorul scriptului (core/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Calea către folderul principal al proiectului
PROJECT_DIR = os.path.join(BASE_DIR, "..")  # urcă un nivel

# Fixed path construction - let the function take file_path as parameter
def get_default_file_path():
    """Returns the default Excel file path"""
    return os.path.join(PROJECT_DIR, "data", "input_samples", "Facturi_Test.xlsx")

def read_excel(file_path=None):
    """Citește fișierul Excel și validează coloanele necesare."""
    if file_path is None:
        file_path = get_default_file_path()
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"✗ Fișierul nu există: {file_path}")
        print(f"✓ Directorul curent: {os.getcwd()}")
        print(f"✓ BASE_DIR: {BASE_DIR}")
        print(f"✓ PROJECT_DIR: {PROJECT_DIR}")
        
        # Try to find the file in current directory or subdirectories
        current_dir = os.getcwd()
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                if file.endswith('.xlsx') and 'Facturi' in file:
                    found_path = os.path.join(root, file)
                    print(f"✓ Am găsit un fișier Excel similar: {found_path}")
        
        return None
    
    try:
        df = pd.read_excel(file_path)
        print(f"✓ Fișierul Excel a fost citit cu succes: {len(df)} înregistrări")
        print(f"✓ Calea fișierului: {os.path.abspath(file_path)}")
    except Exception as e:
        print(f"✗ Eroare la citirea fișierului: {e}")
        return None
    
    # Coloanele necesare pentru generarea facturilor
    required_columns = [
        "Număr factură", "Data emiterii", "Tip factură", "Monedă",
        "Nume vânzător", "ID legal vânzător", "ID TVA vânzător",
        "Stradă vânzător", "Oraș vânzător", "Județ vânzător", "Cod poștal vânzător", "Țară vânzător",
        "Nume cumpărător", "ID legal cumpărător", "ID TVA cumpărător",
        "Stradă cumpărător", "Oraș cumpărător", "Județ cumpărător", "Cod poștal cumpărător", "Țară cumpărător",
        "Termeni plată", "Linii factură (produse)",
        "Valoare totală fără TVA", "Total TVA", "Total plată"
    ]
    
    # Verifică dacă toate coloanele necesare există
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"✗ Lipsesc coloanele: {', '.join(missing)}")
        print("Coloane disponibile în fișier:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        return None
    
    print("✓ Toate coloanele necesare sunt prezente")
    return df

def count_products(lines_str):
    """Numără produsele din coloana 'Linii factură (produse)'."""
    if pd.isna(lines_str) or not lines_str:
        return 0
    # Produsele sunt separate prin „;"
    products = lines_str.split(";")
    return len([p for p in products if p.strip()])  # Numără doar liniile non-goale

def validate_invoice_data(df):
    """Validează datele facturilor și returnează un raport."""
    issues = []
    
    for index, row in df.iterrows():
        invoice_num = row["Număr factură"]
        
        # Verifică dacă sunt produse
        num_products = count_products(row["Linii factură (produse)"])
        if num_products == 0:
            issues.append(f"Factura {invoice_num}: Nu are produse definite")
        
        # Verifică totalurile
        try:
            total_no_vat = float(row["Valoare totală fără TVA"])
            total_vat = float(row["Total TVA"])
            total_payment = float(row["Total plată"])
            
            if abs((total_no_vat + total_vat) - total_payment) > 0.01:
                issues.append(f"Factura {invoice_num}: Totalurile nu se potrivesc")
        except (ValueError, TypeError):
            issues.append(f"Factura {invoice_num}: Valori totale invalide")
        
        # Verifică datele obligatorii
        required_fields = ["Nume vânzător", "Nume cumpărător", "Data emiterii"]
        for field in required_fields:
            if pd.isna(row[field]) or str(row[field]).strip() == "":
                issues.append(f"Factura {invoice_num}: Câmpul '{field}' este gol")
    
    return issues

def print_invoice_summary(df):
    """Afișează un sumar al facturilor."""
    print(f"\n{'='*50}")
    print(f"SUMAR FACTURI - {len(df)} facturi găsite")
    print(f"{'='*50}")
    
    for index, row in df.iterrows():
        inv_num = row["Număr factură"]
        date = row["Data emiterii"]
        seller = row["Nume vânzător"]
        buyer = row["Nume cumpărător"]
        total = row["Total plată"]
        currency = row["Monedă"]
        num_products = count_products(row["Linii factură (produse)"])
        
        print(f"Factura: {inv_num}")
        print(f"  Data: {date}")
        print(f"  Vânzător: {seller}")
        print(f"  Cumpărător: {buyer}")
        print(f"  Produse: {num_products}")
        print(f"  Total: {total} {currency}")
        print("-" * 30)

if __name__ == "__main__":
    print("Citesc fișierul Excel...")
    df = read_excel()
    
    if df is not None:
        # Afișează sumarul facturilor
        print_invoice_summary(df)
        
        # Validează datele
        print(f"\n{'='*50}")
        print("VALIDARE DATE")
        print(f"{'='*50}")
        
        issues = validate_invoice_data(df)
        if issues:
            print("⚠️  Probleme găsite:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ Toate datele sunt valide!")
        
        print(f"\nFacturile sunt gata pentru generarea PDF!")