from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QMessageBox, QHeaderView, QTableWidgetItem, QLabel, QItemDelegate, QAbstractItemView
)
from PySide6.QtGui import QFont, QColor, QKeySequence, QDoubleValidator, QShortcut
from PySide6.QtCore import Qt
import pandas as pd
import core.db_handler as db
import pyperclip
from core import pdf_generator


class DoubleDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        editor.setValidator(validator)
        return editor


class InvoiceTableDialog(QDialog):
    def __init__(self, parent=None, import_data=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice Table - Database Edition")
        self.resize(1200, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(800, 400)
        self.showMaximized()
        self.saved_data = None
        self.undo_stack = []
        self._last_value = None
        self._last_row = None
        self._last_col = None
        self._tracking = False
        self.columns = [
            "Număr factură", "Data emiterii", "Tip factură", "Monedă", "Nume cumpărător",
            "ID legal cumpărător", "ID TVA cumpărător", "Stradă cumpărător", "Oraș cumpărător",
            "Județ cumpărător", "Cod poștal cumpărător", "Țară cumpărător",
            "Termeni plată", "Linii factură (produse)",
            "Valoare totală fără TVA", "Total TVA", "Total plată"
        ]
        layout = QVBoxLayout(self)
        info_text = (
            f"Loaded {len(import_data)} invoices from database"
            if import_data is not None
            else "Creating new invoices - data will be saved to database"
        )
        self.info_label = QLabel(info_text)
        layout.addWidget(self.info_label)
        self.table = QTableWidget(
            max(100, len(import_data) + 20) if import_data is not None else 100,
            len(self.columns)
        )
        self.table.setHorizontalHeaderLabels([
            f"{col} *" if col in ["Număr factură", "Data emiterii", "Nume cumpărător"] else col
            for col in self.columns
        ])
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)
        header = self.table.horizontalHeader()
        header.setFont(header_font)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #5e548e;
                color: white;
            }
        """)
        if import_data is not None:
            self.populate_table_with_data(import_data)
        self.table.cellActivated.connect(self.store_old_value)
        self.table.cellClicked.connect(self.store_old_value)
        self.table.itemChanged.connect(self.track_changes)
        layout.addWidget(self.table)
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shortcut.activated.connect(self.undo_last_edit)
        button_layout = QHBoxLayout()
        if import_data is not None:
            self.generateSelectedBtn = QPushButton("Generate selected invoices to PDFs")
            self.generateSelectedBtn.clicked.connect(self.generate_selected_pdfs)
            buttons = [self.generateSelectedBtn]
        else:
            self.saveToDbButton = QPushButton("Save to Database")
            self.saveToDbButton.clicked.connect(self.save_to_database)
            buttons = [self.saveToDbButton]
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        buttons.append(self.cancelButton)
        button_layout.addStretch()
        for btn in buttons:
            button_layout.addWidget(btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def store_old_value(self, row, col):
        item = self.table.item(row, col)
        self._last_value = item.text() if item else ""
        self._last_row = row
        self._last_col = col

    def track_changes(self, item):
        if self._tracking:
            return
        if self._last_row == item.row() and self._last_col == item.column():
            new_value = item.text()
            if new_value != self._last_value:
                self.undo_stack.append((item.row(), item.column(), self._last_value))
        self._last_value, self._last_row, self._last_col = None, None, None

    def undo_last_edit(self):
        if not self.undo_stack:
            return
        row, col, old_value = self.undo_stack.pop()
        item = self.table.item(row, col)
        if not item:
            item = QTableWidgetItem()
            self.table.setItem(row, col, item)
        self._tracking = True
        item.setText(str(old_value))
        self._tracking = False

    def paste_from_clipboard(self):
        clipboard_text = pyperclip.paste()
        rows = clipboard_text.split("\n")
        current_row, current_col = self.table.currentRow(), self.table.currentColumn()
        for r, row_data in enumerate(rows):
            if not row_data.strip():
                continue
            cols = row_data.split("\t")
            for c, col_data in enumerate(cols):
                item = QTableWidgetItem(col_data.strip())
                self.table.setItem(current_row + r, current_col + c, item)

    def populate_table_with_data(self, data):
        if len(data) > self.table.rowCount():
            self.table.setRowCount(len(data) + 20)
        for row_idx, (_, row_data) in enumerate(data.iterrows()):
            for col_idx, column_name in enumerate(self.columns):
                value = str(row_data[column_name]) if column_name in row_data and pd.notna(row_data[column_name]) else ""
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))
        self.info_label.setText(f"Loaded {len(data)} invoices from database - select rows and generate PDFs")

    def get_selected_invoices(self):
        selected_rows = self.table.selectionModel().selectedRows()
        data = []
        for row in selected_rows:
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row.row(), col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        if data:
            return pd.DataFrame(data, columns=self.columns)
        return None

    def generate_selected_pdfs(self):
        df = self.get_selected_invoices()
        if df is None or df.empty:
            QMessageBox.warning(self, "No Selection", "Please select at least one invoice.")
            return
        errors = self.validate_invoice_data(df)
        if errors:
            msg = "Validation warnings:\n\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n\n...and {len(errors) - 5} more"
            msg += "\n\nDo you want to continue anyway?"
            reply = QMessageBox.question(self, "Validation", msg, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        for _, row in df.iterrows():
            pdf_generator.generate_invoice_from_dict(row.to_dict())
        QMessageBox.information(self, "Success", f"Generated PDFs for {len(df)} selected invoices.")
        self.accept()

    def validate_invoice_data(self, df):
        errors = []
        invalid_cells = []
        for idx, row in df.iterrows():
            invoice_num = row.get("Număr factură", "")
            if not invoice_num.strip():
                errors.append(f"Row {idx + 1}: Missing invoice number")
                invalid_cells.append((idx, self.columns.index("Număr factură")))
                continue
            if not row.get("Data emiterii", "").strip():
                errors.append(f"Invoice {invoice_num}: Missing issue date")
                invalid_cells.append((idx, self.columns.index("Data emiterii")))
            if not row.get("Nume cumpărător", "").strip():
                errors.append(f"Invoice {invoice_num}: Missing buyer name")
                invalid_cells.append((idx, self.columns.index("Nume cumpărător")))
        for row, col in invalid_cells:
            item = self.table.item(row, col)
            if item:
                item.setBackground(QColor(255, 200, 200))
        return errors

    def save_to_database(self):
        df = self.get_selected_invoices()
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                db.insert_invoice(row.to_dict())
            QMessageBox.information(self, "Success", f"{len(df)} invoices saved to database.")
            self.accept()
        else:
            QMessageBox.warning(self, "No Data", "No data to save.")
