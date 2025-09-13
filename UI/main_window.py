from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QFileDialog,
    QMessageBox, QVBoxLayout, QWidget
)
from pathlib import Path

from core import excel_handler, pdf_generator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice App - UI")
        self.setMinimumSize(400, 200)

        self.excel_path = None

        layout = QVBoxLayout()

        self.btn_import = QPushButton("📂 Import Excel")
        self.btn_import.clicked.connect(self.import_excel)
        layout.addWidget(self.btn_import)

        self.btn_pdf = QPushButton("📄 Generează PDF-uri")
        self.btn_pdf.clicked.connect(self.generate_pdfs)
        layout.addWidget(self.btn_pdf)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def import_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Alege un fișier Excel", "", "Excel Files (*.xlsx)"
        )
        if path:
            self.excel_path = Path(path)
            QMessageBox.information(self, "Succes", f"Am ales fișierul:\n{path}")

    def generate_pdfs(self):
        if not self.excel_path:
            QMessageBox.warning(self, "Eroare", "Mai întâi importă un fișier Excel!")
            return

        try:
            invoices = excel_handler.read_excel(self.excel_path)

            count = pdf_generator.generate_pdfs(invoices)

            QMessageBox.information(self, "Succes", f"Am generat {count} facturi PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))
