from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QFileDialog, QMessageBox, QHeaderView, QTableWidgetItem
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import pandas as pd


class InvoiceTableDialog(QDialog):
    def __init__(self, parent=None, import_data=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice Table")
        self.resize(1200, 700)

        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(800, 400)
        self.showMaximized()

        # Track saved data for parent access
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

        # Create table with all columns if importing data
        if import_data is not None:
            self.table = QTableWidget(max(100, len(import_data) + 20), len(self.columns))
        else:
            self.table = QTableWidget(100, len(self.columns))
        
        self.table.setHorizontalHeaderLabels(self.columns)

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

        # Populate table with imported data if provided
        if import_data is not None:
            self.populate_table_with_data(import_data)

        self.table.cellChanged.connect(self.extend_rows_if_needed)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.saveButton = QPushButton("Save")
        self.useDataButton = QPushButton("Use Data")
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
        self.saveButton.setStyleSheet(button_style)
        self.useDataButton.setStyleSheet(button_style)
        self.cancelButton.setStyleSheet(button_style)

        button_layout.addStretch()
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.useDataButton)
        button_layout.addWidget(self.cancelButton)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.saveButton.clicked.connect(self.save_table)
        self.useDataButton.clicked.connect(self.use_data_without_saving)
        self.cancelButton.clicked.connect(self.reject)

    def populate_table_with_data(self, data):
        """Populate the table with imported data"""
        try:
            # Ensure we have enough rows
            if len(data) > self.table.rowCount():
                self.table.setRowCount(len(data) + 20)

            for row_idx, (_, row_data) in enumerate(data.iterrows()):
                for col_idx, column_name in enumerate(self.columns):
                    if column_name in row_data:
                        value = str(row_data[column_name]) if pd.notna(row_data[column_name]) else ""
                        item = QTableWidgetItem(value)
                        self.table.setItem(row_idx, col_idx, item)
                    else:
                        # Set empty item for missing columns
                        item = QTableWidgetItem("")
                        self.table.setItem(row_idx, col_idx, item)

            # Update window title to show imported data
            self.setWindowTitle("Invoice Table - Imported Data")
            
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Error populating table:\n{str(e)}")

    def extend_rows_if_needed(self, row, col):
        if row == self.table.rowCount() - 1:
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
        else:
            return None

    def use_data_without_saving(self):
        """Use the current table data without saving to file"""
        try:
            df = self.get_table_data_as_dataframe()
            if df is not None and not df.empty:
                self.saved_data = df
                self.saved_file_path = None  # No file path since we're not saving
                QMessageBox.information(self, "Success", f"Using {len(df)} rows of data for invoice generation.")
                self.accept()
            else:
                QMessageBox.warning(self, "No Data", "No data found in the table.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not process table data:\n{str(e)}")

    def save_table(self):
        """Save table data to Excel file for compatibility with import"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Table", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if path:
            try:
                df = self.get_table_data_as_dataframe()
                if df is not None and not df.empty:
                    if path.lower().endswith('.xlsx'):
                        # Save as Excel file
                        df.to_excel(path, index=False, engine='openpyxl')
                    else:
                        # Save as CSV file
                        if not path.lower().endswith('.csv'):
                            path += ".csv"
                        df.to_csv(path, index=False, encoding="utf-8-sig")
                    
                    # Store the data for parent access
                    self.saved_data = df
                    self.saved_file_path = path
                    
                    QMessageBox.information(self, "Success", f"Table saved as:\n{path}")
                    self.accept()
                else:
                    QMessageBox.warning(self, "No Data", "No data found in the table to save.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{str(e)}")
