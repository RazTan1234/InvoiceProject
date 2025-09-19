from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QFileDialog, QMessageBox, QHeaderView
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import pandas as pd


class InvoiceTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Invoice Table")
        self.resize(1200, 700)

        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setSizeGripEnabled(True)
        self.setMinimumSize(800, 400)
        self.showMaximized()

        self.columns = [
            "Număr factură",
            "Data emiterii",
            "Tip factură",
            "Monedă",
            "Nume cumpărător",
            "ID legal cumpărător",
            "ID TVA cumpărător",
            "Stradă cumpărător"
        ]

        layout = QVBoxLayout(self)

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

        self.table.cellChanged.connect(self.extend_rows_if_needed)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.saveButton = QPushButton("Save")
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
        self.cancelButton.setStyleSheet(button_style)

        button_layout.addStretch()
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.cancelButton)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.saveButton.clicked.connect(self.save_table)
        self.cancelButton.clicked.connect(self.reject)

    def extend_rows_if_needed(self, row, col):
        if row == self.table.rowCount() - 1:
            self.table.setRowCount(self.table.rowCount() + 20)

    def save_table(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Table", "", "CSV Files (*.csv)"
        )
        if path:
            try:
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

                df = pd.DataFrame(data, columns=self.columns)
                df.to_csv(path, index=False, encoding="utf-8-sig")

                QMessageBox.information(self, "Success", f"Table saved as:\n{path}")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file:\n{e}")
