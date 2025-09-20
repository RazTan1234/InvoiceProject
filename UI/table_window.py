from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QMessageBox, QHeaderView, QTableWidgetItem, QLabel, QItemDelegate
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
import pandas as pd
import core.db_handler as db

class DoubleDelegate(QItemDelegate):
    """Delegate to enforce numeric input for specific columns"""
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

        self.columns = [
            "Număr factură",
            "Data emiterii", 
            "Tip factură",
            "Monedă",
            "Nume cumpărător",
            "ID legal cumpărător",
            "ID TVA cumpărător",
            "Stradă cumpărător",
            "Oraș cumpărător",
            "Județ cumpărător",
            "Cod poștal cumpărător",
            "Țară cumpărător",
            "Termeni plată",
            "Linii factură (produse)",
            "Valoare totală fără TVA",
            "Total TVA",
            "Total plată"
        ]

        layout = QVBoxLayout(self)

        if import_data is not None:
            info_text = f"Editing {len(import_data)} invoices from database"
        else:
            info_text = "Creating new invoices - data will be saved to database"
            
        self.info_label = QLabel(info_text)
        self.info_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #e8f4f8; border-radius: 4px;")
        layout.addWidget(self.info_label)

        if import_data is not None:
            self.table = QTableWidget(max(100, len(import_data) + 20), len(self.columns))
        else:
            self.table = QTableWidget(100, len(self.columns))
        
        self.table.setHorizontalHeaderLabels([f"{col} *" if col in ["Număr factură", "Data emiterii", "Nume cumpărător"] else col for col in self.columns])

        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(10)
        header = self.table.horizontalHeader()
        header.setFont(header_font)

        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        for i, col in enumerate(self.columns):
            self.table.horizontalHeaderItem(i).setToolTip(col)

        # Set numeric validator for total columns
        for col_name in ["Valoare totală fără TVA", "Total TVA", "Total plată"]:
            col_idx = self.columns.index(col_name)
            self.table.setItemDelegateForColumn(col_idx, DoubleDelegate(self))

        if import_data is not None:
            self.populate_table_with_data(import_data)

        self.table.cellChanged.connect(self.extend_rows_if_needed)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        
        if import_data is not None:
            self.updateDbButton = QPushButton("Update Database")
            self.useDataButton = QPushButton("Use for PDF Generation")
        else:
            self.saveToDbButton = QPushButton("Save to Database")
            self.useDataButton = QPushButton("Use for PDF Generation")
        
        self.cancelButton = QPushButton("Cancel")

        button_style = """
            QPushButton {
                background-color: #6A5ACD;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #7B68EE;
            }
            QPushButton:pressed {
                background-color: #483D8B;
            }
        """
        
        if import_data is not None:
            self.updateDbButton.setStyleSheet(button_style)
            button_layout.addWidget(self.updateDbButton)
            self.updateDbButton.clicked.connect(self.update_database)
        else:
            self.saveToDbButton.setStyleSheet(button_style)
            button_layout.addWidget(self.saveToDbButton)
            self.saveToDbButton.clicked.connect(self.save_to_database)
        
        self.useDataButton.setStyleSheet(button_style)
        self.cancelButton.setStyleSheet(button_style)

        button_layout.addStretch()
        button_layout.addWidget(self.useDataButton)
        button_layout.addWidget(self.cancelButton)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.useDataButton.clicked.connect(self.use_data_for_pdf)
        self.cancelButton.clicked.connect(self.reject)

    def populate_table_with_data(self, data):
        """Populate the table with imported data from database"""
        try:
            if len(data) > self.table.rowCount():
                self.table.setRowCount(len(data) + 20)

            for row_idx, (_, row_data) in enumerate(data.iterrows()):
                for col_idx, column_name in enumerate(self.columns):
                    if column_name in row_data:
                        value = str(row_data[column_name]) if pd.notna(row_data[column_name]) else ""
                        item = QTableWidgetItem(value)
                        self.table.setItem(row_idx, col_idx, item)
                    else:
                        item = QTableWidgetItem("")
                        self.table.setItem(row_idx, col_idx, item)

            self.info_label.setText(f"Loaded {len(data)} invoices from database - you can edit and save changes")
            
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Error populating table:\n{str(e)}")

    def extend_rows_if_needed(self, row, col):
        """Add more rows if user is entering data near the bottom"""
        if row >= self.table.rowCount() - 5:
            self.table.setRowCount(self.table.rowCount() + 20)

    def get_table_data_as_dataframe(self):
        """Extract data from table and return as DataFrame"""
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
        """Validate invoice data before saving"""
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
        
        # Highlight invalid cells
        for row, col in invalid_cells:
            item = self.table.item(row, col)
            if item:
                item.setBackground(QColor(255, 200, 200))  # Light red background
        
        return errors

    def save_to_database(self):
        """Save new table data to database"""
        df = self.get_table_data_as_dataframe()
        if df is not None and not df.empty:
            # Clear previous highlights
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 255, 255))
            
            # Validate data
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
                print(f"Database error details: {str(e)}")  # Log for debugging
                QMessageBox.warning(self, "Database Error", f"Error saving to database:\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Data", "No data to save to database.")

    def update_database(self):
        """Placeholder for updating existing database records"""
        QMessageBox.information(self, "Info", "Update functionality will be implemented in future version.\nFor now, this will create new records.")
        self.save_to_database()

    def use_data_for_pdf(self):
        """Use current table data for PDF generation without saving to database"""
        df = self.get_table_data_as_dataframe()
        if df is not None and not df.empty:
            # Clear previous highlights
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