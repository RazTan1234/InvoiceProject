from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QMessageBox, QHeaderView, QTableWidgetItem, QLabel, QItemDelegate
)
from PySide6.QtGui import QFont, QColor, QKeySequence, QDoubleValidator, QShortcut
from PySide6.QtCore import Qt
import pandas as pd
import core.db_handler as db
import pyperclip


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
        self.saved_file_path = None
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
            f"Editing {len(import_data)} invoices from database"
            if import_data is not None
            else "Creating new invoices - data will be saved to database"
        )
        self.info_label = QLabel(info_text)
        self.info_label.setObjectName("infoLabel")
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
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
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
            self.updateDbButton = QPushButton("Update Database")
            self.updateDbButton.setObjectName("updateDbButton")
            self.updateDbButton.clicked.connect(self.update_database)
            buttons = [self.updateDbButton]
        else:
            self.saveToDbButton = QPushButton("Save to Database")
            self.saveToDbButton.setObjectName("saveToDbButton")
            self.saveToDbButton.clicked.connect(self.save_to_database)
            buttons = [self.saveToDbButton]
        self.useDataButton = QPushButton("Use for PDF Generation")
        self.useDataButton.setObjectName("useDataButton")
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setObjectName("cancelButton")
        self.useDataButton.clicked.connect(self.use_data_for_pdf)
        self.cancelButton.clicked.connect(self.reject)
        buttons.extend([self.useDataButton, self.cancelButton])
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
        self._last_value = None
        self._last_row = None
        self._last_col = None

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

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)

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
        try:
            if len(data) > self.table.rowCount():
                self.table.setRowCount(len(data) + 20)
            for row_idx, (_, row_data) in enumerate(data.iterrows()):
                for col_idx, column_name in enumerate(self.columns):
                    if column_name in row_data:
                        value = str(row_data[column_name]) if pd.notna(row_data[column_name]) else ""
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                    else:
                        self.table.setItem(row_idx, col_idx, QTableWidgetItem(""))
            self.info_label.setText(f"Loaded {len(data)} invoices from database - you can edit and save changes")
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Error populating table:\n{str(e)}")

    def extend_rows_if_needed(self, row, col):
        if row >= self.table.rowCount() - 5:
            self.table.setRowCount(self.table.rowCount() + 20)

    def get_table_data_as_dataframe(self):
        rows, cols = self.table.rowCount(), self.table.columnCount()
        data = []
        for row in range(rows):
            row_data = []
            is_empty = True
            for col in range(cols):
                item = self.table.item(row, col)
                value = item.text() if item else ""
                if value.strip():
                    is_empty = False
                row_data.append(value)
            if not is_empty:
                data.append(row_data)
        if data:
            return pd.DataFrame(data, columns=self.columns)
        return None

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
            try:
                total_no_vat = float(row.get("Valoare totală fără TVA", 0) or 0)
                total_vat = float(row.get("Total TVA", 0) or 0)
                total_payment = float(row.get("Total plată", 0) or 0)
                if abs((total_no_vat + total_vat) - total_payment) > 0.01:
                    errors.append(f"Invoice {invoice_num}: Total amounts don't match")
                    invalid_cells.extend([
                        (idx, self.columns.index("Valoare totală fără TVA")),
                        (idx, self.columns.index("Total TVA")),
                        (idx, self.columns.index("Total plată"))
                    ])
            except (ValueError, TypeError):
                errors.append(f"Invoice {invoice_num}: Invalid numeric values in totals")
                invalid_cells.extend([
                    (idx, self.columns.index("Valoare totală fără TVA")),
                    (idx, self.columns.index("Total TVA")),
                    (idx, self.columns.index("Total plată"))
                ])
        for row, col in invalid_cells:
            item = self.table.item(row, col)
            if item:
                item.setBackground(QColor(255, 200, 200))
        return errors

    def save_to_database(self):
        df = self.get_table_data_as_dataframe()
        if df is not None and not df.empty:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))
            errors = self.validate_invoice_data(df)
            if errors:
                error_msg = "Data validation errors:\n\n" + "\n".join(errors[:10])
                if len(errors) > 10:
                    error_msg += f"\n\n...and {len(errors) - 10} more errors"
                QMessageBox.warning(self, "Validation Errors", error_msg)
                return
            try:
                saved_count = 0
                for _, row in df.iterrows():
                    data = {col: row[col] for col in df.columns}
                    db.insert_invoice(data)
                    saved_count += 1
                self.saved_data = df
                self.saved_file_path = None
                QMessageBox.information(self, "Success", f"{saved_count} invoices saved to database successfully!")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Database Error", f"Error saving to database:\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Data", "No data to save to database.")

    def update_database(self):
        QMessageBox.information(
            self, "Info",
            "Update functionality will be implemented in future version.\nFor now, this will create new records."
        )
        self.save_to_database()

    def use_data_for_pdf(self):
        df = self.get_table_data_as_dataframe()
        if df is not None and not df.empty:
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))
            errors = self.validate_invoice_data(df)
            if errors:
                error_msg = "Data validation warnings:\n\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n\n...and {len(errors) - 5} more warnings"
                error_msg += "\n\nDo you want to proceed with PDF generation anyway?"
                reply = QMessageBox.question(self, "Validation Warnings", error_msg,
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            self.saved_data = df
            self.saved_file_path = None
            QMessageBox.information(self, "Success", f"Using {len(df)} invoices for PDF generation.")
            self.accept()
        else:
            QMessageBox.warning(self, "No Data", "No data available for PDF generation.")
