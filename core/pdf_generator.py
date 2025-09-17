from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import pandas as pd
from datetime import datetime

# Director unde salvăm PDF-urile și fontul
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "fonts", "DejaVuSans.ttf")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "output_pdfs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ModernPDFInvoice(FPDF):
    # Culori moderne (RGB)
    BRAND_BLUE = (41, 128, 185)      # #2980B9
    DARK_GRAY = (52, 73, 94)         # #34495E
    LIGHT_GRAY = (236, 240, 241)     # #ECF0F1
    WHITE = (255, 255, 255)
    SUCCESS_GREEN = (39, 174, 96)    # #27AE60
    TEXT_GRAY = (127, 140, 141)      # #7F8C8D
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        # Adăugăm toate stilurile fontului
        self.add_font("DejaVu", "", FONT_PATH)      # normal
        self.add_font("DejaVu", "B", FONT_PATH)    # bold
        self.add_font("DejaVu", "I", FONT_PATH)    # italic
        self.add_font("DejaVu", "BI", FONT_PATH)   # bold-italic
        
        # Header modern cu gradient visual effect
        self.set_fill_color(*self.BRAND_BLUE)
        self.rect(0, 0, 210, 25, 'F')  # Header bar
        
        # Logo/Brand area (simulat)
        self.set_xy(15, 8)
        self.set_text_color(*self.WHITE)
        self.set_font("DejaVu", "B", 18)
        self.cell(0, 10, "YOUR COMPANY", align="L")
        
        # Invoice title
        self.set_xy(140, 8)
        self.set_font("DejaVu", "B", 16)
        self.cell(0, 10, "FACTURĂ", align="R")
        
        # Reset colors
        self.set_text_color(*self.DARK_GRAY)
        self.ln(35)

    def footer(self):
        self.set_y(-20)
        
        # Footer line
        self.set_draw_color(*self.LIGHT_GRAY)
        self.line(15, self.get_y()-5, 195, self.get_y()-5)
        
        # Footer text
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(*self.TEXT_GRAY)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")
        
        # Company tagline
        self.ln(5)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 5, "Mulțumim pentru încrederea acordată!", align="C")

def parse_product_lines(lines_str):
    """Parsează liniile de produse din format string în listă de dicționare."""
    if pd.isna(lines_str) or not lines_str:
        return []
    
    products = []
    lines = lines_str.split(";")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Presupunem format: "Nume produs | Cantitate | Preț unitar | TVA%"
        # Sau adaptat la formatul tău specific
        parts = [part.strip() for part in line.split("|")]
        
        if len(parts) >= 4:
            try:
                product = {
                    "name": parts[0],
                    "quantity": float(parts[1]),
                    "unit_price": float(parts[2]),
                    "vat_rate": float(parts[3])
                }
                product["subtotal"] = product["quantity"] * product["unit_price"]
                product["vat_amount"] = product["subtotal"] * product["vat_rate"] / 100
                product["total"] = product["subtotal"] + product["vat_amount"]
                products.append(product)
            except (ValueError, IndexError):
                # Dacă nu putem parsa linia, o ignorăm
                continue
    
    return products

def create_info_card(pdf, x, y, width, height, title, content, color):
    """Creează un card cu informații stilizat."""
    # Background card
    pdf.set_fill_color(*color)
    pdf.rect(x, y, width, height, 'F')
    
    # Title bar
    pdf.set_fill_color(*pdf.DARK_GRAY)
    pdf.rect(x, y, width, 12, 'F')
    
    # Title
    pdf.set_xy(x + 5, y + 3)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(0, 6, title)
    
    # Content
    pdf.set_xy(x + 5, y + 15)
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "", 9)
    
    line_height = 5
    for line in content:
        pdf.cell(0, line_height, line)
        pdf.ln(line_height)
        pdf.set_x(x + 5)

def safe_get(row, column_name, default="N/A"):
    """Safely get a value from DataFrame row, return default if not exists or empty."""
    try:
        value = row.get(column_name, default)
        if pd.isna(value) or str(value).strip() == "":
            return default
        return str(value)
    except:
        return default

def generate_invoice_pdf(row, seller_settings=None):
    """Generează PDF modern pentru o factură."""
    
    pdf = ModernPDFInvoice()
    pdf.add_page()

    # Reset la poziția după header
    pdf.set_xy(15, 40)

    # === SECȚIUNEA INVOICE INFO ===
    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(15, 40, 180, 25, 'F')

    pdf.set_xy(20, 45)
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 8, f"FACTURĂ #{safe_get(row, 'Număr factură')}")

    pdf.set_font("DejaVu", "", 9)
    pdf.set_xy(20, 55)
    pdf.cell(40, 5, f"Data: {safe_get(row, 'Data emiterii')}")
    pdf.set_xy(80, 55)
    pdf.cell(40, 5, f"Tip: {safe_get(row, 'Tip factură')}")
    pdf.set_xy(140, 55)
    pdf.cell(40, 5, f"Moneda: {safe_get(row, 'Monedă')}")

    pdf.ln(25)

    # === CARDS VÂNZĂTOR ȘI CUMPĂRĂTOR ===
    # Vânzător card - use settings if available, otherwise show placeholder
    if seller_settings:
        seller_content = [
            f"Nume: {seller_settings.get('name', 'Nu este setat')}",
            f"ID Legal: {seller_settings.get('legal_id', 'Nu este setat')}",
            f"ID TVA: {seller_settings.get('vat', 'Nu este setat')}",
        ]
    else:
        seller_content = [
            "Nume: Nu este configurat",
            "ID Legal: Nu este configurat", 
            "ID TVA: Nu este configurat",
            "(Configurați în Settings)"
        ]
    
    create_info_card(pdf, 15, 75, 85, 40, "VÂNZĂTOR", seller_content, pdf.WHITE)

    # Cumpărător card (date din Excel)
    buyer_content = [
        f"{safe_get(row, 'Nume cumpărător')}",
        f"ID Legal: {safe_get(row, 'ID legal cumpărător')}",
        f"ID TVA: {safe_get(row, 'ID TVA cumpărător')}",
        f"{safe_get(row, 'Stradă cumpărător')}",
        f"{safe_get(row, 'Oraș cumpărător')}, {safe_get(row, 'Județ cumpărător')}",
        f"{safe_get(row, 'Cod poștal cumpărător')}, {safe_get(row, 'Țară cumpărător')}"
    ]
    create_info_card(pdf, 110, 75, 85, 50, "CUMPĂRĂTOR", buyer_content, pdf.WHITE)

    # Adjust position after seller card height change
    pdf.set_xy(15, 145)
    pdf.set_fill_color(*pdf.BRAND_BLUE)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(180, 8, f"   Termeni de plată: {safe_get(row, 'Termeni plată')}", 'F')

    pdf.ln(15)

    # === TABEL PRODUSE ===
    pdf.set_fill_color(*pdf.DARK_GRAY)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 9)

    pdf.set_x(15)
    pdf.cell(65, 10, "Produs", 1, align="C", fill=True)
    pdf.cell(18, 10, "Cant.", 1, align="C", fill=True)
    pdf.cell(25, 10, "Preț unitar", 1, align="C", fill=True)
    pdf.cell(22, 10, "Subtotal", 1, align="C", fill=True)
    pdf.cell(15, 10, "TVA%", 1, align="C", fill=True)
    pdf.cell(20, 10, "TVA", 1, align="C", fill=True)
    pdf.cell(25, 10, "Total", 1, align="C", fill=True)
    pdf.ln()

    products = parse_product_lines(safe_get(row, 'Linii factură (produse)', ""))
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "", 8)

    # If no products, show a placeholder row
    if not products:
        pdf.set_fill_color(248, 249, 250)
        pdf.set_x(15)
        pdf.cell(190, 8, "Nu sunt produse definite", 1, align="C", fill=True)
        pdf.ln()
    else:
        for i, product in enumerate(products):
            if i % 2 == 0:
                pdf.set_fill_color(248, 249, 250)
            else:
                pdf.set_fill_color(*pdf.WHITE)

            product_name = product["name"][:28] + "..." if len(product["name"]) > 28 else product["name"]

            pdf.set_x(15)
            pdf.cell(65, 8, product_name, 1, fill=True)
            pdf.cell(18, 8, f'{product["quantity"]:.0f}', 1, align="R", fill=True)
            pdf.cell(25, 8, f'{product["unit_price"]:.2f}', 1, align="R", fill=True)
            pdf.cell(22, 8, f'{product["subtotal"]:.2f}', 1, align="R", fill=True)
            pdf.cell(15, 8, f'{product["vat_rate"]:.0f}%', 1, align="C", fill=True)
            pdf.cell(20, 8, f'{product["vat_amount"]:.2f}', 1, align="R", fill=True)
            pdf.cell(25, 8, f'{product["total"]:.2f}', 1, align="R", fill=True)
            pdf.ln()

    pdf.ln(8)

    # === TOTALURI ===
    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(120, pdf.get_y(), 75, 35, 'F')

    totals_y = pdf.get_y() + 5
    pdf.set_xy(125, totals_y)
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "", 10)
    
    # Safely get numeric values
    try:
        subtotal = float(safe_get(row, 'Valoare totală fără TVA', '0'))
        vat_total = float(safe_get(row, 'Total TVA', '0'))
        total_payment = float(safe_get(row, 'Total plată', '0'))
        currency = safe_get(row, 'Monedă', 'RON')
    except (ValueError, TypeError):
        subtotal = vat_total = total_payment = 0.0
        currency = 'RON'
    
    pdf.cell(65, 7, f"Subtotal: {subtotal:.2f} {currency}", align="R")

    pdf.set_xy(125, totals_y + 8)
    pdf.cell(65, 7, f"TVA: {vat_total:.2f} {currency}", align="R")

    pdf.line(125, totals_y + 17, 190, totals_y + 17)

    pdf.set_xy(120, totals_y + 20)
    pdf.set_fill_color(*pdf.SUCCESS_GREEN)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(75, 10, f"TOTAL: {total_payment:.2f} {currency}", 1, align="C", fill=True)

    # Footer
    pdf.set_xy(15, pdf.get_y() + 25)
    pdf.set_text_color(*pdf.TEXT_GRAY)
    pdf.set_font("DejaVu", "I", 9)
    pdf.cell(0, 5, "Vă mulțumim pentru colaborare și vă așteptăm din nou!", align="C")

    # Salvare PDF
    safe_filename = str(safe_get(row, 'Număr factură', 'UNKNOWN')).replace("/", "_").replace("\\", "_")
    file_path = os.path.join(OUTPUT_DIR, f"Modern_Invoice_{safe_filename}.pdf")
    pdf.output(file_path)

    return file_path


def generate_all_invoices(df, seller_settings=None):
    """Generează PDF-uri pentru toate facturile din DataFrame."""
    generated_files = []
    
    for index, row in df.iterrows():
        try:
            file_path = generate_invoice_pdf(row, seller_settings)
            generated_files.append(file_path)
            print(f"✓ Factura {safe_get(row, 'Număr factură')} generată: {file_path}")
        except Exception as e:
            print(f"✗ Eroare la generarea facturii {safe_get(row, 'Număr factură')}: {e}")
            import traceback
            traceback.print_exc()  # This will help debug the issue
    
    return generated_files

if __name__ == "__main__":
    # Importăm funcția de citire din primul script
    from excel_handler import read_excel
    
    # Calea către fișierul Excel
    PROJECT_DIR = os.path.join(BASE_DIR, "..")
    file_path = os.path.join(PROJECT_DIR, "data/input_samples/Facturi_Test.xlsx")
    
    # Citim datele
    df = read_excel(file_path)
    
    if df is not None:
        print(f"\nGenerez PDF-uri pentru {len(df)} facturi...")
        generated_files = generate_all_invoices(df)
        print(f"\n✓ {len(generated_files)} facturi generate cu succes!")
        print(f"PDF-urile au fost salvate în: {OUTPUT_DIR}")
    else:
        print("Nu s-au putut citi datele din Excel.")