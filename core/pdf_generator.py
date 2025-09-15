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

def generate_invoice_pdf(row):
    """Generează PDF modern pentru o factură."""
    
    pdf = ModernPDFInvoice()
    pdf.add_page()
    
    # Reset la poziția după header
    pdf.set_xy(15, 40)
    
    # === SECȚIUNEA INVOICE INFO ===
    # Informații factură în stil modern card-based
    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(15, 40, 180, 25, 'F')
    
    # Invoice number (prominent)
    pdf.set_xy(20, 45)
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "B", 14)
    pdf.cell(0, 8, f"FACTURĂ #{row['Număr factură']}")
    
    # Info în coloane
    pdf.set_font("DejaVu", "", 9)
    pdf.set_xy(20, 55)
    pdf.cell(40, 5, f"Data: {row['Data emiterii']}")
    pdf.set_xy(80, 55)
    pdf.cell(40, 5, f"Tip: {row['Tip factură']}")
    pdf.set_xy(140, 55)
    pdf.cell(40, 5, f"Moneda: {row['Monedă']}")
    
    pdf.ln(25)
    
    # === CARDS VÂNZĂTOR ȘI CUMPĂRĂTOR ===
    # Vânzător card
    seller_content = [
        f"{row['Nume vânzător']}",
        f"ID Legal: {row['ID legal vânzător']}",
        f"ID TVA: {row['ID TVA vânzător']}",
        f"{row['Stradă vânzător']}",
        f"{row['Oraș vânzător']}, {row['Județ vânzător']}",
        f"{row['Cod poștal vânzător']}, {row['Țară vânzător']}"
    ]
    create_info_card(pdf, 15, 75, 85, 50, "VÂNZĂTOR", seller_content, pdf.WHITE)
    
    # Cumpărător card
    buyer_content = [
        f"{row['Nume cumpărător']}",
        f"ID Legal: {row['ID legal cumpărător']}",
        f"ID TVA: {row['ID TVA cumpărător']}",
        f"{row['Stradă cumpărător']}",
        f"{row['Oraș cumpărător']}, {row['Județ cumpărător']}",
        f"{row['Cod poștal cumpărător']}, {row['Țară cumpărător']}"
    ]
    create_info_card(pdf, 110, 75, 85, 50, "CUMPĂRĂTOR", buyer_content, pdf.WHITE)
    
    # Termeni de plată
    pdf.set_xy(15, 135)
    pdf.set_fill_color(*pdf.BRAND_BLUE)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 9)
    pdf.cell(180, 8, f"   Termeni de plată: {row['Termeni plată']}", 'F')
    
    pdf.ln(15)
    
    # === TABEL PRODUSE MODERN ===
    # Header tabel cu gradient effect
    pdf.set_fill_color(*pdf.DARK_GRAY)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 9)
    
    # Header row
    pdf.set_x(15)
    pdf.cell(65, 10, "Produs", 1, align="C", fill=True)
    pdf.cell(18, 10, "Cant.", 1, align="C", fill=True)
    pdf.cell(25, 10, "Preț unitar", 1, align="C", fill=True)
    pdf.cell(22, 10, "Subtotal", 1, align="C", fill=True)
    pdf.cell(15, 10, "TVA%", 1, align="C", fill=True)
    pdf.cell(20, 10, "TVA", 1, align="C", fill=True)
    pdf.cell(25, 10, "Total", 1, align="C", fill=True)
    pdf.ln()
    
    # Parsare și afișare produse cu alternating colors
    products = parse_product_lines(row['Linii factură (produse)'])
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "", 8)
    
    for i, product in enumerate(products):
        # Alternating row colors
        if i % 2 == 0:
            pdf.set_fill_color(248, 249, 250)  # Very light gray
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
    
    # === TOTALURI FINALE CU DESIGN MODERN ===
    # Background pentru totaluri
    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(120, pdf.get_y(), 75, 35, 'F')
    
    # Totaluri cu stil
    totals_y = pdf.get_y() + 5
    
    pdf.set_xy(125, totals_y)
    pdf.set_text_color(*pdf.DARK_GRAY)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(65, 7, f"Subtotal: {row['Valoare totală fără TVA']:.2f} {row['Monedă']}", align="R")
    
    pdf.set_xy(125, totals_y + 8)
    pdf.cell(65, 7, f"TVA: {row['Total TVA']:.2f} {row['Monedă']}", align="R")
    
    # Linie separator
    pdf.set_draw_color(*pdf.DARK_GRAY)
    pdf.line(125, totals_y + 17, 190, totals_y + 17)
    
    # Total final cu background colorat
    pdf.set_xy(120, totals_y + 20)
    pdf.set_fill_color(*pdf.SUCCESS_GREEN)
    pdf.set_text_color(*pdf.WHITE)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(75, 10, f"TOTAL: {row['Total plată']:.2f} {row['Monedă']}", 1, align="C", fill=True)
    
    # === FOOTER MESSAGE ===
    pdf.set_xy(15, pdf.get_y() + 25)
    pdf.set_text_color(*pdf.TEXT_GRAY)
    pdf.set_font("DejaVu", "I", 9)
    pdf.cell(0, 5, "Vă mulțumim pentru colaborare și vă așteptăm din nou!", align="C")
    
    # Salvare PDF
    safe_filename = str(row['Număr factură']).replace("/", "_").replace("\\", "_")
    file_path = os.path.join(OUTPUT_DIR, f"Modern_Invoice_{safe_filename}.pdf")
    pdf.output(file_path)
    
    return file_path

def generate_all_invoices(df):
    """Generează PDF-uri pentru toate facturile din DataFrame."""
    generated_files = []
    
    for index, row in df.iterrows():
        try:
            file_path = generate_invoice_pdf(row)
            generated_files.append(file_path)
            print(f"✓ Factura {row['Număr factură']} generată: {file_path}")
        except Exception as e:
            print(f"✗ Eroare la generarea facturii {row['Număr factură']}: {e}")
    
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
