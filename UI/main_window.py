import subprocess
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QPushButton, QMessageBox, QVBoxLayout, QWidget, QLabel

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

        self.lbl_file = QLabel("Niciun fișier selectat")
        layout.addWidget(self.lbl_file)

        self.btn_pdf = QPushButton("📄 Generează PDF-uri")
        self.btn_pdf.clicked.connect(self.generate_pdfs)
        layout.addWidget(self.btn_pdf)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def import_excel(self):
        try:
            cmd = [
                "powershell.exe",
                "-Command",
                "[System.Reflection.Assembly]::LoadWithPartialName('System.windows.forms') | Out-Null; "
                "$file = (New-Object System.Windows.Forms.OpenFileDialog -Property @{Filter='Excel Files (*.xlsx)|*.xlsx'}).ShowDialog(); "
                "if ($file -eq 'OK') {Write-Output $($dialog.FileName)}"
            ]
            path = subprocess.check_output(cmd).decode().strip()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", f"Nu am putut deschide Explorer: {e}")
            return

        if path:
            wsl_path = subprocess.check_output(["wslpath", "-a", path]).decode().strip()
            self.excel_path = Path(wsl_path)
            self.lbl_file.setText(f"Fișier selectat: {path}")
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
