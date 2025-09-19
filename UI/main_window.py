from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QLineEdit, QFormLayout, QListWidget
)
from PySide6.QtCore import Qt
import os
import subprocess
import sys
import pandas as pd

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

        self._build_main_page()
        self._build_invoices_list_page()
        self._build_settings_page()

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.excel_data = None
        self.excel_file_path = None
        self.current_settings = {}

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
        self.companyName.setPlaceholderText("Company name")
        self.companyCUI = QLineEdit()
        self.companyCUI.setPlaceholderText("CUI")
        layout.addRow("Company:", self.companyName)
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
            self.import_excel()
        elif clicked == open_btn:
            self.open_excel()

    def open_excel(self):
        dialog = InvoiceTableDialog(self)
        dialog.exec()

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
            seller_settings = None
            if hasattr(self, 'current_settings') and self.current_settings:
                seller_settings = self.current_settings.get('seller', {})
                if 'company' in self.current_settings:
                    seller_settings['name'] = self.current_settings['company'].get('name', '')
            generated_files = pdf_generator.generate_all_invoices(self.excel_data, seller_settings)
            if len(generated_files) > 0:
                self._show_info(f"Successfully generated {len(generated_files)} PDF invoices!\n\nFiles saved to: data/output_pdfs/")
                self.load_pdfs()
                self.tabs.setCurrentWidget(self.invoicesListPage)
            else:
                self._show_error("No PDF files were generated. Please check your data.")
        except Exception as e:
            self._show_error(f"Error generating PDFs:\n{str(e)}")

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
            self._show_info("Settings saved successfully!")
            self.current_settings = settings
        except Exception as e:
            self._show_error(f"Could not save settings:\n{e}")

    def load_settings_from_file(self):
        try:
            loaded = settings_handler.load_settings()
            if not isinstance(loaded, dict):
                loaded = {}
            self.current_settings = loaded
        except Exception as e:
            print("Error loading settings:", e)
            self.current_settings = {}
        self.populate_settings_form(self.current_settings)

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
