# gui.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QFileDialog, QHeaderView, QCalendarWidget, QGroupBox
)
from PyQt5.QtCore import Qt, QRegExp, QDate
from PyQt5.QtGui import QRegExpValidator, QIcon, QPalette, QColor, QFont
import sys
import re
import datetime

from .editor import InvoiceGenerator  # Assuming editor.py is in the same directory

class InvoiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Invoice Generator')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Company and Client info form group
        form_groupbox = QGroupBox("Company and Client Information")
        form_layout = QFormLayout()

        self.venue_address_input = QLineEdit()
        self.client_name_input = QLineEdit()
        self.client_phone_input = QLineEdit()
        self.client_email_input = QLineEdit()

        # Validating email input
        email_validator = QRegExpValidator(QRegExp(r'^[\w\.]+@[a-zA-Z_]+\.[a-zA-Z]{2,3}$'))
        self.client_email_input.setValidator(email_validator)

        self.bill_to_name_input = QLineEdit()
        self.invoice_date_calendar = QCalendarWidget()
        self.invoice_date_calendar.setSelectedDate(QDate.currentDate())

        form_layout.addRow(QLabel('Venue Address:'), self.venue_address_input)
        form_layout.addRow(QLabel('Client Name:'), self.client_name_input)
        form_layout.addRow(QLabel('Client Phone:'), self.client_phone_input)
        form_layout.addRow(QLabel('Client Email:'), self.client_email_input)
        form_layout.addRow(QLabel('Bill To (Name):'), self.bill_to_name_input)
        form_layout.addRow(QLabel('Invoice Date:'), self.invoice_date_calendar)

        form_groupbox.setLayout(form_layout)
        main_layout.addWidget(form_groupbox)

        # Items input area group
        items_groupbox = QGroupBox("Invoice Items")
        items_layout = QVBoxLayout()

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Description", "Unit Price", "Quantity"])
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        add_item_layout = QHBoxLayout()
        self.item_name_input = QLineEdit()
        self.item_description_input = QLineEdit()
        self.item_unit_price_input = QLineEdit()
        self.item_unit_price_input.setValidator(QRegExpValidator(QRegExp(r'^\d*\.?\d+$')))
        self.item_quantity_input = QLineEdit()
        self.item_quantity_input.setValidator(QRegExpValidator(QRegExp(r'^\d+$')))

        add_item_layout.addWidget(QLabel('Name:'))
        add_item_layout.addWidget(self.item_name_input)
        add_item_layout.addWidget(QLabel('Description:'))
        add_item_layout.addWidget(self.item_description_input)
        add_item_layout.addWidget(QLabel('Unit Price:'))
        add_item_layout.addWidget(self.item_unit_price_input)
        add_item_layout.addWidget(QLabel('Quantity:'))
        add_item_layout.addWidget(self.item_quantity_input)

        add_item_button = QPushButton('Add Item')
        add_item_button.clicked.connect(self.add_item)
        add_item_layout.addWidget(add_item_button)

        items_layout.addWidget(self.items_table)
        items_layout.addLayout(add_item_layout)
        items_groupbox.setLayout(items_layout)

        main_layout.addWidget(items_groupbox)

        # Generate invoice button
        generate_button = QPushButton('Generate Invoice')
        generate_button.clicked.connect(self.generate_invoice)
        main_layout.addWidget(generate_button)

        self.setLayout(main_layout)

        # Apply custom styles
        self.apply_custom_styles()

    def apply_custom_styles(self):
        # Set custom palette colors
        palette = self.palette()

        # Set colors from heaviest to lightest
        palette.setColor(QPalette.Window, QColor("#2C3E50"))         # Main window background
        palette.setColor(QPalette.AlternateBase, QColor("#34495E"))  # Group box background
        palette.setColor(QPalette.Button, QColor("#1ABC9C"))         # Button background (changed color)
        palette.setColor(QPalette.ButtonText, QColor("#ECF0F1"))     # Button text color

        # Set text colors
        palette.setColor(QPalette.WindowText, QColor("#ECF0F1"))     # Text color for labels
        palette.setColor(QPalette.Text, QColor("#ECF0F1"))           # Text color for input fields

        self.setPalette(palette)

        # Set font
        font = QFont()
        font.setPointSize(10)  # Set default font size for all widgets
        self.setFont(font)

        # Apply font and palette to all child widgets
        def apply_style(widget):
            if isinstance(widget, QWidget):
                widget.setPalette(palette)
                widget.setFont(font)
                for child in widget.findChildren(QWidget):
                    apply_style(child)

        apply_style(self)

        # Apply styles specifically to QGroupBox widgets
        self.setStyleSheet("""
            QGroupBox {
                background-color: #34495E;
                border: 1px solid #ECF0F1;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QLabel {
                color: #ECF0F1;
            }
            QLineEdit, QTableWidget, QCalendarWidget {
                background-color: #2C3E50;
                color: #000;
                border: 1px solid #1ABC9C;  # Updated border color
            }
            QPushButton {
                background-color: #1ABC9C;  # Updated button color
                color: #ECF0F1;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #16A085;  # Updated hover color
                color: #ECF0F1;
            }
            QPushButton:pressed {
                background-color: #148F77;  # Updated pressed color
                color: #ECF0F1;
            }
            QCalendarWidget QWidget {
                background-color: #2C3E50;  # Calendar widget background
                color: #ECF0F1;  # Calendar widget text color
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #1ABC9C;  # Selected date background
                selection-color: #ECF0F1;  # Selected date text color
            }
            QCalendarWidget QToolButton {
                background-color: #1ABC9C;  # Calendar buttons background
                color: #ECF0F1 !important;  # Calendar buttons text color
                border: none;  # Remove border
                border-radius: 5px;  # Add border-radius
            }
            QCalendarWidget QToolButton:hover {
                background-color: #16A085;  # Hover color for calendar buttons
            }
            QCalendarWidget QToolButton:pressed {
                background-color: #148F77;  # Pressed color for calendar buttons
            }
            
        """)

    def add_item(self):
        name = self.item_name_input.text()
        description = self.item_description_input.text()
        unit_price = self.item_unit_price_input.text()
        quantity = self.item_quantity_input.text()

        if not name or not description or not unit_price or not quantity:
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        try:
            unit_price = float(unit_price)
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for Unit Price and Quantity.")
            return

        row_position = self.items_table.rowCount()
        self.items_table.insertRow(row_position)
        self.items_table.setItem(row_position, 0, QTableWidgetItem(name))
        self.items_table.setItem(row_position, 1, QTableWidgetItem(description))
        self.items_table.setItem(row_position, 2, QTableWidgetItem(f"PKR {unit_price:.2f}"))
        self.items_table.setItem(row_position, 3, QTableWidgetItem(str(quantity)))

        # Clear input fields
        self.item_name_input.clear()
        self.item_description_input.clear()
        self.item_unit_price_input.clear()
        self.item_quantity_input.clear()

    def generate_invoice(self):
        venue_address = self.venue_address_input.text()
        client_name = self.client_name_input.text()
        client_phone = self.client_phone_input.text()
        client_email = self.client_email_input.text()
        bill_to_name = self.bill_to_name_input.text()
        invoice_date = self.invoice_date_calendar.selectedDate().toString(Qt.ISODate)

        items = []
        for row in range(self.items_table.rowCount()):
            item = {
                "name": self.items_table.item(row, 0).text(),
                "description": self.items_table.item(row, 1).text(),
                "unit_price": float(self.items_table.item(row, 2).text().replace("PKR ", "")),
                "quantity": int(self.items_table.item(row, 3).text())
            }
            items.append(item)

        if not all([venue_address, client_name, client_phone, client_email, bill_to_name, items]):
            QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
            return

        company_info = {
            "name": "My Company",
            "address": venue_address,
            "email": "info@mycompany.com",
            "phone": "+123456789"
        }
        client_info = {
            "name": client_name,
            "bill_to": bill_to_name,
            "email": client_email,
            "phone": client_phone
        }
        invoice_info = {
            "invoice_number": "INV12345",
            "date": invoice_date
        }
        logo_path = "logo_resized.png"  # Path to the resized logo image

        try:
            invoice_generator = InvoiceGenerator(company_info, client_info, items, invoice_info, logo_path)
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Invoice PDF", "invoice.pdf", "PDF Files (*.pdf)")
            if save_path:
                invoice_generator.save_pdf(save_path)
                QMessageBox.information(self, "Invoice Generated", f"Invoice saved successfully at:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while generating the invoice:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply Fusion style
    app.setStyle('Fusion')

    # Create an instance of InvoiceGUI
    window = InvoiceGUI()

    # Set window icon (assuming 'icon.png' is in the same directory)
    window.setWindowIcon(QIcon('icon.png'))

    # Show the GUI
    window.show()

    # Execute the application
    sys.exit(app.exec_())
