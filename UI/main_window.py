from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QLineEdit, QFormLayout, QListWidget
)
from PySide6.QtCore import Qt
import os
import subprocess
import sys
import pandas as pd
from PySide6.QtWidgets import QVBoxLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core import excel_handler, pdf_generator, settings_handler
from UI.table_window import InvoiceTableDialog

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
        self.tabs.addTab(self.mainPage, "Main")
        self.tabs.addTab(self.invoicesListPage, "Invoices")
        self.tabs.addTab(self.settingsPage, "Settings")
        self.aboutPage = QWidget()
        self.tabs.addTab(self.aboutPage, "About Us")
        self.statsPage = QWidget()
        self.tabs.addTab(self.statsPage, "Statistics")
        self._build_main_page()
        self._build_about_page()
        self._build_stats_page()
        self._build_invoices_list_page()
        self._build_settings_page()
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.excel_data = None
        self.excel_file_path = None
        self.current_settings = self.load_settings_from_file()

    def _build_stats_page(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Statistics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        title.setAlignment(Qt.AlignCenter)

        # Labels pentru statistici
        self.totalInvoicesLabel = QLabel("Total invoices: 0")
        self.totalInvoicesLabel.setStyleSheet("font-size: 14px; color: #fff;")
        self.totalAmountLabel = QLabel("Total amount: 0 RON")
        self.totalAmountLabel.setStyleSheet("font-size: 14px; color: #fff;")

        # Canvas pentru grafic
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
                "Invoice App v1.0\n\n"
                "Această aplicație a fost creată pentru a simplifica generarea facturilor PDF.\n\n"
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
        if sys.platform.startswith("linux"):
            if "microsoft" in os.uname().release.lower():
                if filepath.startswith("/mnt/"):
                    drive = filepath[5]
                    win_path = drive.upper() + ":" + filepath[6:]
                    win_path = win_path.replace("/", "\\")
                else:
                    win_path = filepath.replace("/", "\\")
                subprocess.Popen(["cmd.exe", "/c", "start", "", win_path])
            else:
                subprocess.Popen(["xdg-open", filepath])
        elif sys.platform == "win32":
            os.startfile(filepath)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", filepath])

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


    def show_write_invoices_popup(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Write Invoices")
        msg.setText("Choose an option:")
        msg.setIcon(QMessageBox.Question)
        import_btn = msg.addButton("Import File", QMessageBox.AcceptRole)
        open_btn = msg.addButton("New Table", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == import_btn:
            self.import_and_show_table()
        elif clicked == open_btn:
            self.open_excel()

    def open_excel(self):
        dialog = InvoiceTableDialog(self)
        if dialog.exec():
            if hasattr(dialog, 'saved_data') and dialog.saved_data is not None:
                self.excel_data = dialog.saved_data
                self.excel_file_path = dialog.saved_file_path
                filename = os.path.basename(dialog.saved_file_path) if dialog.saved_file_path else "New Table"
                rows_count = len(self.excel_data)
                self.fileLabel.setText(f"✓ {filename}")
                if rows_count > 0:
                    self._show_info(f"Successfully created {rows_count} invoices from table")

    def import_and_show_table(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Import", "", "Data Files (*.xlsx *.xls *.csv)"
        )
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    data = pd.read_csv(file_path)
                else:
                    data = excel_handler.read_excel(file_path)
                if data is not None:
                    dialog = InvoiceTableDialog(self, import_data=data)
                    if dialog.exec():
                        if hasattr(dialog, 'saved_data') and dialog.saved_data is not None:
                            self.excel_data = dialog.saved_data
                            self.excel_file_path = dialog.saved_file_path
                            filename = os.path.basename(dialog.saved_file_path) if dialog.saved_file_path else "Imported Table"
                            rows_count = len(self.excel_data)
                            self.fileLabel.setText(f"✓ {filename}")
                            if rows_count > 0:
                                self._show_info(f"Successfully imported and processed {rows_count} invoices from {filename}")
                else:
                    self._show_error("Failed to read file. Please check the format and required columns.")
            except Exception as e:
                self._show_error(f"Error importing file:\n{str(e)}")

    def import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "Data Files (*.xlsx *.xls *.csv)"
        )
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.excel_data = pd.read_csv(file_path)
                else:
                    self.excel_data = excel_handler.read_excel(file_path)
                if self.excel_data is not None:
                    self.excel_file_path = file_path
                    filename = os.path.basename(file_path)
                    rows_count = len(self.excel_data)
                    self.fileLabel.setText(f"✓ {filename}")
                    if rows_count > 0:
                        self._show_info(f"Successfully imported {rows_count} invoices from {filename}")
                    else:
                        self._show_info(f"File imported successfully but contains no invoices.")
                else:
                    self.fileLabel.setText("✗ Failed to load file")
                    self._show_error("Failed to read file. Please check the format and required columns.")
            except Exception as e:
                self.fileLabel.setText("✗ Error loading file")
                self._show_error(f"Error importing file:\n{str(e)}")

    def generate_pdfs(self):
        if self.excel_data is None or self.excel_data.empty:
            self._show_error("Please import a file first!")
            return
        try:
            user_settings = settings_handler.load_settings()
            if not user_settings.get('company', {}).get('name') or not user_settings.get('seller', {}):
                self._show_warning("Settings are incomplete. Some seller fields may show 'Nu este setat'.")
            self.current_settings = user_settings
            print(f"Generating PDFs with settings: {user_settings}")
            generated_files = pdf_generator.generate_all_invoices(self.excel_data, user_settings)
            if generated_files:
                self._show_info(
                    f"Successfully generated {len(generated_files)} PDF invoices!\n\nFiles saved to: data/output_pdfs/"
                )
                self.load_pdfs()
                self.tabs.setCurrentWidget(self.invoicesListPage)
            else:
                self._show_error("No PDF files were generated. Please check your data.")
        except Exception as e:
            self._show_error(f"Error generating PDFs:\n{str(e)}")

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
            self._show_error(f"Could not save settings:\n{e}")

    def load_settings_from_file(self):
        try:
            loaded = settings_handler.load_settings()
            if not isinstance(loaded, dict):
                loaded = {}
            print(f"Loaded settings: {loaded}")
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