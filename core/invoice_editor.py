from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt
import pandas as pd
import json
import os

from pdf_generator import generate_all_invoices

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, "..")
JSON_PATH = os.path.join(PROJECT_DIR, "data", "input_samples", "invoices.json")

class InvoiceEditor(QDialog):
    def __init__(self, parent=None, seller_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice Editor")
        self.resize(1200, 600)
        self.seller_settings = seller_settings

        # Coloanele predefinite (din excel_handler)
        self.columns = [
            "Număr factură", "Data emiterii", "Tip factură", "Monedă",
            "Nume cumpărător", "ID legal cumpărător", "ID TVA cumpărător",
            "Stradă cumpărător", "Oraș cumpărător", "Județ cumpărător", 
            "Cod poștal cumpărător", "Țară cumpărător",
            "Termeni plată", "Linii factură (produse)",
            "Valoare totală fără TVA", "Total TVA", "Total plată"
        ]

        # Tabelul
        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Butoane
        add_row_btn = QPushButton("Add Row")
        remove_row_btn = QPushButton("Remove Selected Row")
        save_generate_btn = QPushButton("Save to JSON & Generate PDFs")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(add_row_btn)
        btn_layout.addWidget(remove_row_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_generate_btn)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Conexiuni
        add_row_btn.clicked.connect(self.add_row)
        remove_row_btn.clicked.connect(self.remove_row)
        save_generate_btn.clicked.connect(self.save_and_generate)

        # Încarcă din JSON dacă există
        self.load_from_json()

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        # Precompletează cu valori default dacă vrei (ex: Monedă = "RON")
        self.table.setItem(row_position, 3, QTableWidgetItem("RON"))  # Monedă default

    def remove_row(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self.table.removeRow(row)
        else:
            QMessageBox.warning(self, "Warning", "Select a row to remove.")

    def get_table_data(self):
        data = []
        for row in range(self.table.rowCount()):
            row_data = {}
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data[self.columns[col]] = item.text() if item else ""
            data.append(row_data)
        return data

    def save_and_generate(self):
        data = self.get_table_data()
        if not data:
            QMessageBox.warning(self, "Warning", "No data to save or generate.")
            return

        # Salvează în JSON
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Converti în DataFrame pentru pdf_generator
        df = pd.DataFrame(data)

        # Generează PDF-uri
        try:
            generated_files = generate_all_invoices(df, self.seller_settings)
            if generated_files:
                QMessageBox.information(self, "Success", f"Generated {len(generated_files)} PDFs!\nSaved to: data/output_pdfs/")
                self.parent().load_pdfs()  # Reîncarcă lista de PDF-uri în tab-ul Invoices
                self.parent().tabs.setCurrentWidget(self.parent().invoicesListPage)
            else:
                QMessageBox.warning(self, "Warning", "No PDFs generated. Check data.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating PDFs:\n{str(e)}")

        self.close()  # Închide dialogul după succes

    def load_from_json(self):
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.table.setRowCount(len(data))
            for row_idx, row_data in enumerate(data):
                for col_idx, col_name in enumerate(self.columns):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(row_data.get(col_name, "")))