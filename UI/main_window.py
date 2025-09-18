from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QLineEdit, QFormLayout, QListWidget, QTextEdit
)
from PySide6.QtCore import Qt
import os
import subprocess
import sys
from core import excel_handler, pdf_generator, settings_handler, excel_template
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice App")
        self.resize(900, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.mainPage = QWidget()
        self.invoicesListPage = QWidget()
        self.settingsPage = QWidget()

        self.aboutPage = QWidget()  # New About page

        self.chartsPage = QWidget()  # new Charts page

        self.tabs.addTab(self.mainPage, "Main")
        self.tabs.addTab(self.aboutPage, "About")
        self.tabs.addTab(self.invoicesListPage, "Invoices")
        self.tabs.addTab(self.chartsPage, "Charts")
        self.tabs.addTab(self.settingsPage, "Settings")

        self._build_main_page()
        self._build_invoices_list_page()
        self._build_settings_page()
        self._build_about_page()
        self._build_charts_page()

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.excel_data = None
        self.excel_file_path = None
        self.current_settings = {}

    def _build_charts_page(self):
        layout = QVBoxLayout()
        
        # create matplotlib figure
        self.figure = Figure(figsize=(6,4))
        self.canvas = FigureCanvas(self.figure)
        
        layout.addWidget(self.canvas)
        self.chartsPage.setLayout(layout)
        
        # optional: plot an initial example chart
        self.plot_example_chart()

    def plot_example_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot([1,2,3,4,5], [10,20,15,25,30], marker='o')
        ax.set_title("Example Chart")
        ax.set_xlabel("X-axis")
        ax.set_ylabel("Y-axis")
        self.canvas.draw()
    
    def _build_about_page(self):
        layout = QVBoxLayout()
        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setText("""
            <h2>About Invoice App</h2>
            <p><b>Version:</b> 1.0.0</p>
            <p><b>Description:</b> A simple application for creating and managing invoices.</p>
            <p><b>Author:</b> Your Name</p>
            <p><b>Contact:</b> your.email@example.com</p>
            <p><b>License:</b> MIT License</p>
            <p>Built with PySide6, pandas, and fpdf2.</p>
        """)
        about_text.setStyleSheet("QTextEdit { border: 1px solid #ECF0F1; border-radius: 5px; padding: 10px; }")
        layout.addWidget(about_text)
        layout.addStretch()
        self.aboutPage.setLayout(layout)

    def _build_main_page(self):
        self.writeInvoicesButton = QPushButton("Write Invoices")
        self.writeInvoicesButton.setObjectName("writeInvoicesButton")

        self.generateButton = QPushButton("Generate PDFs")
        self.generateButton.setObjectName("generateButton")

        buttonLayout = QHBoxLayout()
        buttonLayout.setSpacing(30)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.writeInvoicesButton)
        buttonLayout.addWidget(self.generateButton)
        buttonLayout.addStretch()

        self.writeInvoicesButton.clicked.connect(self.show_write_invoices_popup)
        self.fileLabel = QLabel("No file selected")
        self.fileLabel.setObjectName("fileLabel")
        self.fileLabel.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addLayout(buttonLayout)
        layout.addWidget(self.fileLabel, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.invoicesPage.setLayout(layout)
        self.generateButton.clicked.connect(self.generate_pdfs)
    
    def show_write_invoices_popup(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Write Invoices")
        msg.setText("Choose an option:")
        msg.setIcon(QMessageBox.Question)

        import_btn = msg.addButton("Import Excel", QMessageBox.AcceptRole)
        open_btn = msg.addButton("New Excel", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)

        msg.exec()

        clicked = msg.clickedButton()
        if clicked == import_btn:
            self.import_excel()
        elif clicked == open_btn:
            self.open_excel()
        else:
            pass  # Cancel

    def _build_settings_page(self):
        layout = QFormLayout()

        # Company
        self.companyName = QLineEdit()
        self.companyName.setPlaceholderText("Company name")
        self.companyCUI = QLineEdit()
        self.companyCUI.setPlaceholderText("CUI")
        layout.addRow("Company:", self.companyName)
        layout.addRow("CUI:", self.companyCUI)

        # Seller fields
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

        # Save button
        self.saveSettingsButton = QPushButton("Save Settings")
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

        # Connect save button
        self.saveSettingsButton.clicked.connect(self.save_settings)
        self.settingsPage.setLayout(layout)
        self.load_settings_from_file()

    def open_excel(self):
        file_path = excel_template.create_excel_template()
        self._show_info(f"Excel template creat și deschis:\n{file_path}")
        
    def import_excel(self):
        """Import Excel file using the correct function name"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                # Use the correct function name: read_excel (not load_excel)
                self.excel_data = excel_handler.read_excel(file_path)
                
                if self.excel_data is not None:
                    self.excel_file_path = file_path
                    filename = os.path.basename(file_path)
                    self.fileLabel.setText(f"✓ {filename}")
                    self._show_info(f"Successfully imported {len(self.excel_data)} invoices from {filename}")
                else:
                    self.fileLabel.setText("✗ Failed to load file")
                    self._show_error("Failed to read Excel file. Please check the file format and required columns.")
                    
            except Exception as e:
                self.fileLabel.setText("✗ Error loading file")
                self._show_error(f"Error importing Excel file:\n{str(e)}")
                print(f"Import error: {e}")  # Debug info
        else:
            self.fileLabel.setText("No file selected")

    def generate_pdfs(self):
        """Generate PDFs from the imported Excel data"""
        if self.excel_data is None or self.excel_data.empty:
            self._show_error("Please import an Excel file first!")
            return

        try:
            # Load current settings to pass to PDF generator
            seller_settings = None
            if hasattr(self, 'current_settings') and self.current_settings:
                seller_settings = self.current_settings.get('seller', {})
                # Add company name to seller settings if available
                if 'company' in self.current_settings:
                    seller_settings['name'] = self.current_settings['company'].get('name', '')
            
            # Use the updated function from pdf_generator with seller settings
            generated_files = pdf_generator.generate_all_invoices(self.excel_data, seller_settings)
            count = len(generated_files)
            
            if count > 0:
                self._show_info(f"Successfully generated {count} PDF invoices!\n\nFiles saved to: data/output_pdfs/")
            else:
                self._show_error("No PDF files were generated. Please check your Excel data.")
                
        except Exception as e:
            self._show_error(f"Error generating PDFs:\n{str(e)}")
            print(f"PDF generation error: {e}")  # Debug info

    def _show_error(self, message):
        """Show error message dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def _show_info(self, message):
        """Show info message dialog"""
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
            self._show_info("Settings saved successfully!")
            self.current_settings = settings
        except Exception as e:
            self._show_error(f"Could not save settings:\n{e}")
            print("Save settings error:", e)

    def load_settings_from_file(self):
        """Încarcă settings din JSON în self.current_settings și populează UI"""
        try:
            loaded = settings_handler.load_settings()
            if not isinstance(loaded, dict):
                loaded = {}
            self.current_settings = loaded
        except Exception as e:
            print("Error loading settings:", e)
            self.current_settings = {}

        # Populează câmpurile (setează doar ce nu e None; null din JSON devine None)
        self.populate_settings_form(self.current_settings)

    def populate_settings_form(self, settings: dict):
        """Setează text în QLineEdit-urile formului pentru setările curente."""
        def g(*keys):
            d = settings
            for k in keys:
                if not isinstance(d, dict):
                    return None
                d = d.get(k)
            return d

        # company
        self.companyName.setText(g("company", "name") or "")
        self.companyCUI.setText(g("company", "cui") or "")

        # seller
        self.sellerLegalId.setText(g("seller", "legal_id") or "")
        self.sellerVAT.setText(g("seller", "vat") or "")
        self.sellerStreet.setText(g("seller", "street") or "")
        self.sellerCity.setText(g("seller", "city") or "")
        self.sellerCounty.setText(g("seller", "county") or "")
        self.sellerCountry.setText(g("seller", "country") or "")

    def on_tab_changed(self, index: int):
        """Când tab-ul se schimbă, dacă e Settings reîncărcăm din fișier (în caz că s-a modificat extern)."""
        if index == self.tabs.indexOf(self.settingsPage):
            self.load_settings_from_file()