from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QMessageBox, QVBoxLayout, QWidget, QLabel,
    QStackedWidget, QToolBar, QLineEdit, QFormLayout
)
from PySide6.QtGui import QAction
from pathlib import Path
import subprocess
from core import excel_handler, pdf_generator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice App")
        self.setMinimumSize(800, 500)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.page_invoices = QWidget()
        self.page_settings = QWidget()
        self.stack.addWidget(self.page_invoices)
        self.stack.addWidget(self.page_settings)

        self._setup_invoices_page()
        self._setup_settings_page()

        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        btn_invoices = QAction("Invoices", self)
        btn_invoices.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_invoices))
        toolbar.addAction(btn_invoices)

        btn_settings = QAction("Settings", self)
        btn_settings.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_settings))
        toolbar.addAction(btn_settings)

        self.excel_path = None

    def _setup_invoices_page(self):
        layout = QVBoxLayout()

        self.btn_import = QPushButton("📥 Import Excel")
        self.btn_import.clicked.connect(self.import_excel)
        layout.addWidget(self.btn_import)

        self.btn_pdf = QPushButton("📑 Generate PDFs")
        self.btn_pdf.clicked.connect(self.generate_pdfs)
        layout.addWidget(self.btn_pdf)

        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setStyleSheet("color: #bbb; font-size: 12px;")
        layout.addWidget(self.lbl_file)

        container = QWidget()
        container.setLayout(layout)
        self.page_invoices.setLayout(layout)

    def _setup_settings_page(self):
        layout = QFormLayout()

        self.input_company = QLineEdit()
        self.input_company.setPlaceholderText("Company name")
        layout.addRow("Company:", self.input_company)

        self.input_cui = QLineEdit()
        self.input_cui.setPlaceholderText("CUI")
        layout.addRow("CUI:", self.input_cui)

        self.input_address = QLineEdit()
        self.input_address.setPlaceholderText("Company address")
        layout.addRow("Address:", self.input_address)

        container = QWidget()
        container.setLayout(layout)
        self.page_settings.setLayout(layout)

    def import_excel(self):
        cmd = [
            "powershell.exe",
            "-Command",
            "[System.Reflection.Assembly]::LoadWithPartialName('System.windows.forms') | Out-Null;"
            "$f = New-Object System.Windows.Forms.OpenFileDialog;"
            "$f.Filter = 'Excel Files (*.xlsx;*.xls)|*.xlsx;*.xls';"
            "if ($f.ShowDialog() -eq 'OK') {Write-Output $f.FileName}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        path = result.stdout.strip()

        if path:
            self.excel_path = Path(path)
            self.lbl_file.setText(f"Selected file: {path}")
            QMessageBox.information(self, "Success", f"File selected:\n{path}")

    def generate_pdfs(self):
        if not self.excel_path:
            QMessageBox.warning(self, "Error", "Please import an Excel file first!")
            return

        try:
            invoices = excel_handler.read_excel(self.excel_path)
            count = pdf_generator.generate_pdfs(invoices)
            QMessageBox.information(self, "Success", f"Generated {count} PDF invoices.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
