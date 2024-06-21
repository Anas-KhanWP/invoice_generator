from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QHeaderView
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
import re

from fpdf import FPDF

class RoundedRectPDF(FPDF):
    def rounded_rect(self, x, y, w, h, r, style=''):
        k = self.k
        hp = self.h
        self._out(f'{x * k:.2f} {hp - y * k:.2f} m')
        self._arc(x + w - r, y, x + w, y + r, x + w, y)
        self._arc(x + w, y + h - r, x + w - r, y + h, x + w, y + h)
        self._arc(x + r, y + h, x, y + h - r, x, y + h)
        self._arc(x, y + r, x + r, y, x, y)
        if style == 'F':
            self._out(f'{x * k:.2f} {hp - y * k:.2f} l f')
        elif style == 'FD' or style == 'DF':
            self._out(f'{x * k:.2f} {hp - y * k:.2f} l B')
        else:
            self._out(f'{x * k:.2f} {hp - y * k:.2f} l S')

    def _arc(self, x1, y1, x2, y2, x3, y3):
        h = self.h
        self._out(f'{x1 * self.k:.2f} {h - y1 * self.k:.2f} {x2 * self.k:.2f} {h - y2 * self.k:.2f} {x3 * self.k:.2f} {h - y3 * self.k:.2f} c')


class InvoiceGenerator:
    def __init__(self, company_info, client_info, items, invoice_info, logo_path):
        self.company_info = company_info
        self.client_info = client_info
        self.items = items
        self.invoice_info = invoice_info
        self.logo_path = logo_path
        self.pdf = RoundedRectPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.create_invoice()

    def create_invoice(self):
        self.pdf.add_page()
        self.add_invoice_title()
        self.add_header()
        self.add_items()
        self.add_total()
        self.add_additional_notes()
        self.save_pdf()

    def add_invoice_title(self):
        self.pdf.set_fill_color(0, 0, 0)  # Black background
        self.pdf.set_text_color(255, 255, 255)  # White text
        self.pdf.set_font("Arial", "B", size=16)
        self.pdf.cell(0, 10, "Invoice", ln=True, align='C', fill=True)
        self.pdf.ln(10)

    def add_header(self):
        self.pdf.set_text_color(0, 0, 0)  # Reset to black text
        self.pdf.set_font("Arial", size=12)

        # Logo on the left
        self.pdf.image(self.logo_path, x=10, y=28, w=50)

        # Invoice details on the right
        self.pdf.set_xy(138, 28)
        self.pdf.cell(40, 10, txt=f"Invoice Number: {self.invoice_info['invoice_number']}", ln=True)
        self.pdf.set_xy(138, self.pdf.get_y())
        self.pdf.cell(40, 10, txt=f"Date: {self.invoice_info['date']}", ln=True)
        self.pdf.set_xy(138, self.pdf.get_y())
        self.pdf.cell(40, 10, txt=f"Venue: {self.company_info['address']}", ln=True)
        self.pdf.ln(10)

        # Client info below the logo
        self.pdf.set_y(80)  # Move below the logo
        self.pdf.cell(100, 10, txt=f"Client Name: {self.client_info['name']}", ln=True)
        self.pdf.cell(100, 10, txt=f"Phone: {self.client_info['phone']}", ln=True)
        self.pdf.cell(100, 10, txt=f"Bill To: {self.client_info['bill_to']}", ln=True)
        self.pdf.ln(10)

    def add_items(self):
        self.pdf.set_font("Arial", size=11)  # Set font size to 75% of default
        col_width = 38
        row_height = 10
        margin_left = 10
        margin_top = 5
        radius = 2

        # Adjust starting position for margins
        self.pdf.set_x(margin_left)
        self.pdf.set_y(self.pdf.get_y() + margin_top)

        # Table header with rounded corners
        self.pdf.set_fill_color(238, 238, 238)  # Background color for header
        self.pdf.set_text_color(0, 0, 0)  # Text color for header
        self.pdf.set_draw_color(187, 187, 187)  # Border color for header
        headers = ["Item", "Description", "Unit Price", "Quantity", "Total"]
        
        for header in headers:
            x = self.pdf.get_x()
            y = self.pdf.get_y()
            self.pdf.rounded_rect(x, y, col_width, row_height, radius, 'DF')
            self.pdf.cell(col_width, row_height, header, border=1, fill=True)
        self.pdf.ln(row_height + 2)  # Add some space below header

        # Table rows
        self.pdf.set_fill_color(255, 255, 255)  # Background color for cells
        self.pdf.set_draw_color(221, 221, 221)  # Border color for cells
        for item in self.items:
            self.pdf.set_x(margin_left)
            self.pdf.cell(col_width, row_height, item["name"], border=1)
            self.pdf.cell(col_width, row_height, item["description"], border=1)
            self.pdf.cell(col_width, row_height, f"PKR {item['unit_price']:.2f}", border=1)
            self.pdf.cell(col_width, row_height, str(item["quantity"]), border=1)
            total_price = item['unit_price'] * item['quantity']
            self.pdf.cell(col_width, row_height, f"PKR {total_price:.2f}", border=1)
            self.pdf.ln()

    def add_total(self):
        total_amount = sum(item['unit_price'] * item['quantity'] for item in self.items)
        self.pdf.ln(10)
        self.pdf.set_font("Arial", "B", size=12)
        self.pdf.cell(140, 10, txt="Total Amount:", border=1)
        self.pdf.cell(50, 10, txt=f"PKR {total_amount:.2f}", border=1)
        self.pdf.ln(30)  # Add some space before drawing the line
        
        self.pdf.set_font("Arial", "B", size=17)
        self.pdf.cell(0, 10, "Additional Notes", align='C', ln=True)

        # Draw a line
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(10)  # Add some space after the line

    def add_additional_notes(self):
        self.pdf.set_font("Arial", size=12)
        self.pdf.multi_cell(0, 10, "A finance charge of 1.5% will be made on unpaid balances after 30 days.")
        self.pdf.ln(10)

    def save_pdf(self, filename="invoice.pdf"):
        self.pdf.output(filename)


class InvoiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Invoice Generator')
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()

        # Company and Client info form
        form_layout = QFormLayout()

        self.venue_address_input = QLineEdit()
        self.client_name_input = QLineEdit()
        self.client_phone_input = QLineEdit()
        self.bill_to_name_input = QLineEdit()

        # Validating email input
        email_validator = QRegExpValidator(QRegExp(r'^[\w\.]+@[a-zA-Z_]+\.[a-zA-Z]{2,3}$'))

        self.client_email_input = QLineEdit()
        self.client_email_input.setValidator(email_validator)

        form_layout.addRow('Venue Address:', self.venue_address_input)
        form_layout.addRow('Client Name:', self.client_name_input)
        form_layout.addRow('Client Phone:', self.client_phone_input)
        form_layout.addRow('Client Email:', self.client_email_input)
        form_layout.addRow('Bill To (Name):', self.bill_to_name_input)

        main_layout.addLayout(form_layout)

        # Items input area
        items_layout = QVBoxLayout()
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Item Name", "Description", "Unit Price", "Quantity"])
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        items_layout.addWidget(self.items_table)

        add_item_layout = QHBoxLayout()
        self.item_name_input = QLineEdit()
        self.item_description_input = QLineEdit()
        self.item_unit_price_input = QLineEdit()
        self.item_unit_price_input.setValidator(QRegExpValidator(QRegExp(r'^\d*\.?\d+$')))  # Only allow numbers and decimals
        self.item_quantity_input = QLineEdit()
        self.item_quantity_input.setValidator(QRegExpValidator(QRegExp(r'^\d+$')))  # Only allow whole numbers
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
        items_layout.addLayout(add_item_layout)

        main_layout.addLayout(items_layout)

        # Generate invoice button
        generate_button = QPushButton('Generate Invoice')
        generate_button.clicked.connect(self.generate_invoice)
        main_layout.addWidget(generate_button)

        self.setLayout(main_layout)

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
            "bill_to": bill_to_name,  # Combine bill to with client name
            "email": client_email,
            "phone": client_phone
        }
        invoice_info = {
            "invoice_number": "INV12345",
            "date": "2024-06-21"
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
    window = InvoiceGUI()
    window.show()
    sys.exit(app.exec_())
