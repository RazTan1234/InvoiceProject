from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import pandas as pd
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "fonts", "DejaVuSans.ttf")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "data", "output_pdfs")
USER_SETTINGS_PATH = os.path.join(BASE_DIR, "..", "data", "user_settings.json")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_user_settings():
    """Load user settings from JSON"""
    if not os.path.exists(USER_SETTINGS_PATH):
        print(f"⚠️ user_settings.json not found at {USER_SETTINGS_PATH}")
        return {}
    try:
        with open(USER_SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
        print(f"✅ user_settings.json loaded successfully")
        return settings
    except Exception as e:
        print(f"⚠️ Error reading user_settings.json: {e}")
        return {}

class ModernPDFInvoice(FPDF):
    BRAND_BLUE = (41, 128, 185)
    DARK_GRAY = (52, 73, 94)
    LIGHT_GRAY = (236, 240, 241)
    WHITE = (255, 255, 255)
    SUCCESS_GREEN = (39, 174, 96)
    TEXT_GRAY = (127, 140, 141)
    
    def __init__(self, company_name="YOUR COMPANY"):
        super().__init__()
        self.company_name = company_name
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        if not hasattr(self, '_fonts_added'):
            try:
                self.add_font("DejaVu", "", FONT_PATH)
                self.add_font("DejaVu", "B", FONT_PATH)
                self.add_font("DejaVu", "I", FONT_PATH)
                self._fonts_added = True
            except Exception as e:
                print(f"Warning: Could not load custom font: {e}")
        
        self.set_fill_color(*self.BRAND_BLUE)
        self.rect(0, 0, 210, 25, 'F')
        
        self.set_xy(15, 8)
        self.set_text_color(*self.WHITE)
        try:
            self.set_font("DejaVu", "B", 18)
        except:
            self.set_font("Arial", "B", 18)
        self.cell(0, 10, self.company_name, align="L")
        
        self.set_xy(140, 8)
        try:
            self.set_font("DejaVu", "B", 16)
        except:
            self.set_font("Arial", "B", 16)
        self.cell(0, 10, "FACTURĂ", align="R")
        
        self.set_text_color(*self.DARK_GRAY)
        self.ln(35)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(*self.LIGHT_GRAY)
        self.line(15, self.get_y()-5, 195, self.get_y()-5)
        try:
            self.set_font("DejaVu", "I", 9)
        except:
            self.set_font("Arial", "I", 9)
        self.set_text_color(*self.TEXT_GRAY)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")
        self.ln(5)
        try:
            self.set_font("DejaVu", "", 8)
        except:
            self.set_font("Arial", "", 8)
        self.cell(0, 5, "Mulțumim pentru încrederea acordată!", align="C")

def parse_product_lines(lines_str):
    """Parse product lines from the database format"""
    if pd.isna(lines_str) or not lines_str:
        return []
    
    products = []
    lines = lines_str.split(";")
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
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
                continue
    
    return products

def create_info_card(pdf, x, y, width, height, title, content, color):
    """Create an information card on the PDF"""
    pdf.set_fill_color(*color)
    pdf.rect(x, y, width, height, 'F')
    pdf.set_fill_color(*pdf.DARK_GRAY)
    pdf.rect(x, y, width, 12, 'F')
    pdf.set_xy(x + 5, y + 3)
    pdf.set_text_color(*pdf.WHITE)
    try:
        pdf.set_font("DejaVu", "B", 10)
    except:
        pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, title)
    pdf.set_xy(x + 5, y + 15)
    pdf.set_text_color(*pdf.DARK_GRAY)
    try:
        pdf.set_font("DejaVu", "", 9)
    except:
        pdf.set_font("Arial", "", 9)
    line_height = 5
    for line in content:
        pdf.cell(0, line_height, line)
        pdf.ln(line_height)
        pdf.set_x(x + 5)

def safe_get(row, column_name, default="N/A"):
    """Safely get value from row data"""
    try:
        value = row.get(column_name, default)
        if pd.isna(value) or str(value).strip() == "":
            return default
        return str(value)
    except:
        return default

def generate_invoice_pdf(row, user_settings=None):
    """Generate PDF for a single invoice from database data"""
    user_settings = user_settings or {}
    company = user_settings.get('company', {})
    seller = user_settings.get('seller', {})
    
    company_name = company.get('name', "YOUR COMPANY")
    pdf = ModernPDFInvoice(company_name=company_name)
    pdf.add_page()
    pdf.set_xy(15, 40)

    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(15, 40, 180, 25, 'F')
    pdf.set_xy(20, 45)
    pdf.set_text_color(*pdf.DARK_GRAY)
    try:
        pdf.set_font("DejaVu", "B", 14)
    except:
        pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, f"FACTURĂ #{safe_get(row, 'Număr factură')}")
    try:
        pdf.set_font("DejaVu", "", 9)
    except:
        pdf.set_font("Arial", "", 9)

    # Seller and Buyer info
    seller_content = [
        f"Nume: {seller.get('name', 'Nu este setat')}",
        f"ID legal: {seller.get('legal_id', 'Nu este setat')}",
        f"ID TVA: {seller.get('vat', 'Nu este setat')}",
        f"Stradă: {seller.get('street', 'Nu este setat')}",
        f"{seller.get('city', 'Nu este setat')}, {seller.get('county', 'Nu este setat')}",
        f"{seller.get('country', 'Nu este setat')}"
    ]
    create_info_card(pdf, 15, 75, 85, 50, "VÂNZĂTOR", seller_content, pdf.WHITE)

    buyer_content = [
        f"Nume: {safe_get(row, 'Nume cumpărător')}",
        f"ID legal: {safe_get(row, 'ID legal cumpărător')}",
        f"ID TVA: {safe_get(row, 'ID TVA cumpărător')}",
        f"Stradă: {safe_get(row, 'Stradă cumpărător')}",
        f"{safe_get(row, 'Oraș cumpărător')}, {safe_get(row, 'Județ cumpărător')}",
        f"{safe_get(row, 'Cod poștal cumpărător')}, {safe_get(row, 'Țară cumpărător')}"
    ]
    create_info_card(pdf, 110, 75, 85, 50, "CUMPĂRĂTOR", buyer_content, pdf.WHITE)

    pdf.set_xy(15, 145)
    pdf.set_fill_color(*pdf.BRAND_BLUE)
    pdf.set_text_color(*pdf.WHITE)
    try:
        pdf.set_font("DejaVu", "B", 9)
    except:
        pdf.set_font("Arial", "B", 9)
    pdf.cell(180, 8, f"   Termeni de plată: {safe_get(row, 'Termeni plată')}", 'F')
    pdf.ln(15)

    pdf.set_fill_color(*pdf.DARK_GRAY)
    pdf.set_text_color(*pdf.WHITE)
    try:
        pdf.set_font("DejaVu", "B", 9)
    except:
        pdf.set_font("Arial", "B", 9)
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
    try:
        pdf.set_font("DejaVu", "", 8)
    except:
        pdf.set_font("Arial", "", 8)

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

    pdf.set_fill_color(*pdf.LIGHT_GRAY)
    pdf.rect(120, pdf.get_y(), 75, 35, 'F')
    totals_y = pdf.get_y() + 5
    pdf.set_xy(125, totals_y)
    pdf.set_text_color(*pdf.DARK_GRAY)
    try:
        pdf.set_font("DejaVu", "", 10)
    except:
        pdf.set_font("Arial", "", 10)
    
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
    try:
        pdf.set_font("DejaVu", "B", 12)
    except:
        pdf.set_font("Arial", "B", 12)
    pdf.cell(75, 10, f"TOTAL: {total_payment:.2f} {currency}", 1, align="C", fill=True)

    pdf.set_xy(15, pdf.get_y() + 25)
    pdf.set_text_color(*pdf.TEXT_GRAY)
    try:
        pdf.set_font("DejaVu", "I", 9)
    except:
        pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 5, "Vă mulțumim pentru colaborare și vă așteptăm din nou!", align="C")

    safe_filename = str(safe_get(row, 'Număr factură', 'UNKNOWN')).replace("/", "_").replace("\\", "_")
    file_path = os.path.join(OUTPUT_DIR, f"Invoice_{safe_filename}.pdf")
    
    try:
        pdf.output(file_path)
        return file_path
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None

def generate_all_invoices(df, user_settings=None):
    """Generate PDFs for all invoices in the DataFrame"""
    generated_files = []
    
    if df is None or df.empty:
        print("No data to generate PDFs from")
        return generated_files
    
    print(f"Starting PDF generation for {len(df)} invoices...")
    
    for index, row in df.iterrows():
        try:
            file_path = generate_invoice_pdf(row, user_settings)
            if file_path:
                generated_files.append(file_path)
                print(f"✅ Invoice {row.get('Număr factură', 'N/A')} generated: {os.path.basename(file_path)}")
            else:
                print(f"❌ Failed to generate invoice {row.get('Număr factură', 'N/A')}")
        except Exception as e:
            print(f"❌ Error generating invoice {row.get('Număr factură', 'N/A')}: {e}")
    
    print(f"PDF generation complete: {len(generated_files)} files created")
    return generated_files

if __name__ == "__main__":
    from core import db_handler
    df = db_handler.get_all_invoices()
    if df is not None and not df.empty:
        print(f"\nGenerating PDFs for {len(df)} invoices from database...")
        user_settings = load_user_settings()
        generated_files = generate_all_invoices(df, user_settings)
        print(f"\n✅ {len(generated_files)} invoices generated successfully!")
        print(f"PDFs saved in: {OUTPUT_DIR}")
    else:
        print("No invoices found in database. Add some invoices first.")