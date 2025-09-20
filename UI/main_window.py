from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QLineEdit, QFormLayout, QListWidget
)
from PySide6.QtCore import Qt
import os
import subprocess
import sys
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core import db_handler, pdf_generator, settings_handler
from UI.table_window import InvoiceTableDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice App - Database Edition")
        self.resize(900, 600)
        
        # Initialize database
        db_handler.create_db()
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.mainPage = QWidget()
        self.invoicesListPage = QWidget()
        self.settingsPage = QWidget()
        self.aboutPage = QWidget()
        self.statsPage = QWidget()
        
        self.tabs.addTab(self.mainPage, "Main")
        self.tabs.addTab(self.invoicesListPage, "Invoices")
        self.tabs.addTab(self.settingsPage, "Settings")
        self.tabs.addTab(self.aboutPage, "About Us")
        self.tabs.addTab(self.statsPage, "Statistics")
        
        self._build_main_page()
        self._build_about_page()
        self._build_stats_page()
        self._build_invoices_list_page()
        self._build_settings_page()
        
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.invoice_data = None
        self.current_settings = self.load_settings_from_file()

    def _build_stats_page(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Statistics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        title.setAlignment(Qt.AlignCenter)

        self.totalInvoicesLabel = QLabel("Total invoices: 0")
        self.totalInvoicesLabel.setStyleSheet("font-size: 14px; color: #fff;")
        self.totalAmountLabel = QLabel("Total amount: 0 RON")
        self.totalAmountLabel.setStyleSheet("font-size: 14px; color: #fff;")

        self.figure = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.totalInvoicesLabel)
        layout.addWidget(self.totalAmountLabel)
        layout.addWidget(self.canvas)

        self.statsPage.setLayout(layout)
        
    def _build_about_page(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("About Us")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        title.setAlignment(Qt.AlignCenter)

        content = QLabel(
            "Invoice App v2.0 - Database Edition\n\n"
            "Această aplicație folosește o bază de date SQLite pentru stocarea facturilor.\n\n"
            "Datele sunt gestionate exclusiv în baza de date, fără dependențe de fișiere Excel/CSV.\n\n"
            "Echipa noastră se concentrează pe soluții software eficiente, moderne și intuitive.\n\n"
            "Contact: support@invoiceapp.com"
        )
        content.setWordWrap(True)
        content.setStyleSheet("font-size: 14px; color: #fff;")
        content.setAlignment(Qt.AlignTop)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(content)

        self.aboutPage.setLayout(layout)

    def _build_main_page(self):
        self.newInvoiceButton = QPushButton("New Invoice")
        self.newInvoiceButton.setObjectName("newInvoiceButton")
        self.loadFromDbButton = QPushButton("Load from Database")
        self.loadFromDbButton.setObjectName("loadFromDbButton")
        self.generateButton = QPushButton("Generate PDFs")
        self.generateButton.setObjectName("generateButton")
        
        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(30)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.newInvoiceButton)
        buttonLayout.addWidget(self.loadFromDbButton)
        buttonLayout.addWidget(self.generateButton)
        buttonLayout.addStretch()
        
        self.newInvoiceButton.clicked.connect(self.show_new_invoice_table)
        self.loadFromDbButton.clicked.connect(self.load_from_database)
        
        self.statusLabel = QLabel("Ready - No invoices loaded")
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(buttonLayout)
        layout.addWidget(self.statusLabel, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.mainPage.setLayout(layout)
        self.generateButton.clicked.connect(self.generate_pdfs)

    def _build_invoices_list_page(self):
        layout = QVBoxLayout()
        self.pdfList = QListWidget()
        layout.addWidget(self.pdfList)
        self.invoicesListPage.setLayout(layout)
        self.load_pdfs()
        self.pdfList.itemDoubleClicked.connect(self.open_pdf)

    def load_pdfs(self):
        self.pdfList.clear()
        folder = "data/output_pdfs"
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(".pdf"):
                    self.pdfList.addItem(file)

    def open_pdf(self, item):
        filepath = os.path.abspath(os.path.join("data/output_pdfs", item.text()))
        try:
            if sys.platform.startswith("linux"):
                if "microsoft" in os.uname().release.lower():
                    if filepath.startswith("/mnt/"):
                        drive = filepath[5]
                        win_path = drive.upper() + ":" + filepath[6:].replace("/", "\\")
                    else:
                        win_path = filepath.replace("/", "\\")
                    subprocess.run(["cmd.exe", "/c", "start", "", win_path], check=True)
                else:
                    subprocess.run(["xdg-open", filepath], check=True)
            elif sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                subprocess.run(["open", filepath], check=True)
        except Exception as e:
            self._show_error(f"Failed to open PDF: {e}")

    def _build_settings_page(self):
        layout = QFormLayout()

        self.companyName = QLineEdit()
        self.companyName.setPlaceholderText("Nume companie")
        self.companyCUI = QLineEdit()
        self.companyCUI.setPlaceholderText("CUI")
        layout.addRow("Companie:", self.companyName)
        layout.addRow("CUI:", self.companyCUI)

        self.sellerLegalId = QLineEdit()
        self.sellerLegalId.setPlaceholderText("ID legal vânzător")
        self.sellerVAT = QLineEdit()
        self.sellerVAT.setPlaceholderText("ID TVA vânzător")
        self.sellerStreet = QLineEdit()
        self.sellerStreet.setPlaceholderText("Stradă vânzător")
        self.sellerCity = QLineEdit()
        self.sellerCity.setPlaceholderText("Oraș vânzător")
        self.sellerCounty = QLineEdit()
        self.sellerCounty.setPlaceholderText("Județ vânzător")
        self.sellerCountry = QLineEdit()
        self.sellerCountry.setPlaceholderText("Țară vânzător")

        layout.addRow("ID legal vânzător:", self.sellerLegalId)
        layout.addRow("ID TVA vânzător:", self.sellerVAT)
        layout.addRow("Stradă vânzător:", self.sellerStreet)
        layout.addRow("Oraș vânzător:", self.sellerCity)
        layout.addRow("Județ vânzător:", self.sellerCounty)
        layout.addRow("Țară vânzător:", self.sellerCountry)

        self.saveSettingsButton = QPushButton("Salvează setările")
        self.saveSettingsButton.setObjectName("saveSettingsButton")
        self.saveSettingsButton.setMinimumWidth(160)

        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.saveSettingsButton)
        btn_layout.addStretch()
        btn_layout.setContentsMargins(0, 12, 0, 12)
        btn_container.setLayout(btn_layout)
        layout.addRow(btn_container)

        self.saveSettingsButton.clicked.connect(self.save_settings)
        self.settingsPage.setLayout(layout)
        self.load_settings_from_file()

    def show_new_invoice_table(self):
        """Show empty table for creating new invoices"""
        dialog = InvoiceTableDialog(self)
        if dialog.exec():
            if hasattr(dialog, 'saved_data') and dialog.saved_data is not None:
                self.invoice_data = dialog.saved_data
                rows_count = len(self.invoice_data)
                self.statusLabel.setText(f"✓ {rows_count} new invoices ready for PDF generation")
                self._show_info(f"Successfully created {rows_count} invoices")

    def load_from_database(self):
        """Load existing invoices from database"""
        try:
            df = db_handler.get_all_invoices()
            if df is not None and not df.empty:
                dialog = InvoiceTableDialog(self, import_data=df)
                if dialog.exec():
                    if hasattr(dialog, 'saved_data') and dialog.saved_data is not None:
                        self.invoice_data = dialog.saved_data
                        rows_count = len(self.invoice_data)
                        self.statusLabel.setText(f"✓ Loaded {rows_count} invoices from database")
                        self._show_info(f"Successfully loaded {rows_count} invoices from database")
            else:
                self.statusLabel.setText("Database is empty")
                self._show_info("No invoices found in the database. Create new invoices first.")
        except Exception as e:
            self._show_error(f"Error loading invoices from database: {e}")

    def generate_pdfs(self):
        """Generate PDF invoices from current data"""
        if self.invoice_data is None or self.invoice_data.empty:
            self._show_error("Please load invoices from database or create new ones first!")
            return
        
        try:
            user_settings = settings_handler.load_settings()
            if not user_settings.get('company', {}).get('name') or not user_settings.get('seller', {}):
                self._show_warning("Settings are incomplete. Some seller fields may show 'Nu este setat'.")
            
            self.current_settings = user_settings
            generated_files = pdf_generator.generate_all_invoices(self.invoice_data, user_settings)
            if generated_files:
                self._show_info(
                    f"Successfully generated {len(generated_files)} PDF invoices!\n\n"
                    f"Files saved to: data/output_pdfs/"
                )
                self.load_pdfs()
                self.tabs.setCurrentWidget(self.invoicesListPage)
                self.update_stats()
            else:
                self._show_error("No PDF files were generated. Please check your data.")
                
        except Exception as e:
            self._show_error(f"Error generating PDFs: {e}")

    def update_stats(self):
        """Update statistics display"""
        try:
            stats = db_handler.get_invoice_stats()
            
            self.totalInvoicesLabel.setText(f"Total invoices: {stats['total_count']}")
            self.totalAmountLabel.setText(f"Total amount: {stats['total_amount']:.2f} RON")
            
            if stats['monthly_data']:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                
                months = [data[0] for data in stats['monthly_data'][-6:]]
                amounts = [data[2] for data in stats['monthly_data'][-6:]]
                
                ax.bar(months, amounts, color='#6A5ACD')
                ax.set_title('Monthly Invoice Amounts (Last 6 Months)')
                ax.set_ylabel('Amount (RON)')
                ax.tick_params(axis='x', rotation=45)
                
                self.figure.tight_layout()
                self.canvas.draw()
                
        except Exception as e:
            print(f"Error updating stats: {e}")

    def _show_warning(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec()

    def _show_error(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def _show_info(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.exec()

    def save_settings(self):
        settings = {
            "company": {
                "name": self.companyName.text() or None,
                "cui": self.companyCUI.text() or None,
            },
            "seller": {
                "legal_id": self.sellerLegalId.text() or None,
                "vat": self.sellerVAT.text() or None,
                "street": self.sellerStreet.text() or None,
                "city": self.sellerCity.text() or None,
                "county": self.sellerCounty.text() or None,
                "country": self.sellerCountry.text() or None,
            }
        }
        try:
            settings_handler.save_settings(settings)
            self.current_settings = settings
            self._show_info("Settings saved successfully!")
        except Exception as e:
            self._show_error(f"Could not save settings: {e}")

    def load_settings_from_file(self):
        try:
            loaded = settings_handler.load_settings()
            if not isinstance(loaded, dict):
                loaded = {}
            self.populate_settings_form(loaded)
            return loaded
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def populate_settings_form(self, settings: dict):
        def g(*keys):
            d = settings
            for k in keys:
                if not isinstance(d, dict):
                    return None
                d = d.get(k)
            return d
            
        self.companyName.setText(g("company", "name") or "")
        self.companyCUI.setText(g("company", "cui") or "")
        self.sellerLegalId.setText(g("seller", "legal_id") or "")
        self.sellerVAT.setText(g("seller", "vat") or "")
        self.sellerStreet.setText(g("seller", "street") or "")
        self.sellerCity.setText(g("seller", "city") or "")
        self.sellerCounty.setText(g("seller", "county") or "")
        self.sellerCountry.setText(g("seller", "country") or "")

    def on_tab_changed(self, index: int):
        if index == self.tabs.indexOf(self.settingsPage):
            self.load_settings_from_file()
        elif index == self.tabs.indexOf(self.invoicesListPage):
            self.load_pdfs()
        elif index == self.tabs.indexOf(self.statsPage):
            self.update_stats()