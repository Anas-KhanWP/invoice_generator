# editor.py
from fpdf import FPDF
import json
from .database import insert_invoice, update_invoice_file_path, create_connection

class RoundedRectPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_size = 12  # Set a default font size

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
    
    def get_string_width(self, s):
        return len(s) * self.font_size / 2.54
        
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
        
        invoice_number = self.invoice_info['invoice_number']
        file_path = f"{invoice_number}.pdf"
        self.save_pdf(file_path)
        
        # Update the database with the file path
        update_invoice_file_path(invoice_number, file_path)

        # Save invoice details to the database
        items_json = json.dumps(self.items)
        insert_invoice(self.client_info["name"], self.client_info["phone"], self.client_info["email"],
                       self.client_info["bill_to"], items_json, self.invoice_info["invoice_number"],
                       self.invoice_info["date"], sum(item['unit_price'] * item['quantity'] for item in self.items),
                       file_path)

    def add_invoice_title(self):
        title = 'Invoice'
        title_width = self.pdf.get_string_width(title)
        x_center = (self.pdf.w - title_width) / 2
        
        # Set fill color for the background
        self.pdf.set_fill_color(0, 0, 0)
        self.pdf.set_text_color(255, 255, 255)
        
        # Draw a full-width rectangle for the background
        self.pdf.rounded_rect(10, 10, self.pdf.w - 20, 15, 3, 'F')
        
        # Print centered title
        self.pdf.set_xy(0, 5)
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(self.pdf.w, 10, title, 0, 0, 'C', 1)

    # Explanation:
    # - `title_width` calculates the width of the title string.
    # - `x_center` calculates the horizontal position to center the title within the PDF page width (`self.pdf.w`).
    # - `set_fill_color` sets the background color to black.
    # - `set_text_color` sets the text color to white.
    # - `rounded_rect` draws a rounded rectangle with a full width (self.pdf.w - 20) and fixed height (15) at coordinates (10, 10).
    # - `set_xy` sets the position at (0, 12) to start printing the title, aligning it vertically centered within the rectangle.
    # - `cell` prints the title text (`title`) with center alignment ('C') and applies the background fill (1).



    def add_header(self):
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_font('Arial', '', 12)
        
        # Logo on the left below the invoice title
        self.pdf.image(self.logo_path, x=15, y=25, w=50)
        
        # Invoice number, venue, and date in column format on the right
        self.pdf.set_xy(130, 25)
        self.pdf.cell(0, 10, f'Invoice Number: {self.invoice_info["invoice_number"]}', 0, 1)
        self.pdf.set_xy(130, 32)
        self.pdf.cell(0, 10, f'Venue: {self.company_info["address"]}', 0, 1)
        self.pdf.set_xy(130, 39)
        self.pdf.cell(0, 10, f'Date: {self.invoice_info["date"]}', 0, 1)
        self.pdf.ln(10)

        # Client info on the right side below invoice details
        self.pdf.set_xy(15, 80)
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(0, 10, 'Bill To:', 0, 1)
        # self.pdf.cell(0, 10, f'Name: {self.client_info["bill_to"]}', 0, 1)
        self.pdf.cell(0, 10, f'Client Name: {self.client_info["name"]}', 0, 1)
        self.pdf.cell(0, 10, f'Email: {self.client_info["email"]}', 0, 1)
        self.pdf.cell(0, 10, f'Phone: {self.client_info["phone"]}', 0, 1)
        self.pdf.ln(10)

    def add_items(self):
        self.pdf.set_font('Arial', 'B', 12)
        self.pdf.cell(0, 10, 'Items', 0, 1)
        self.pdf.set_font('Arial', '', 12)

        # Set up table headers
        col_widths = [50, 50, 30, 30, 30]
        headers = ['Item Name', 'Description', 'Unit Price', 'Quantity', 'Total']
        for i in range(len(headers)):
            self.pdf.cell(col_widths[i], 10, headers[i], 1, 0, 'L')
        self.pdf.ln()

        # Add items
        for item in self.items:
            # Calculate total for each item
            total_item = item['unit_price'] * item['quantity']

            # Measure height required for the description
            x = self.pdf.get_x()
            y = self.pdf.get_y()
            self.pdf.multi_cell(col_widths[1], 10, item['description'], 1)
            description_height = self.pdf.get_y() - y

            # Ensure all cells in the row have the same height
            row_height = max(10, description_height)

            # Reset Y position for consistent row height
            self.pdf.set_xy(x, y)

            # Write cells with adjusted row height
            self.pdf.cell(col_widths[0], row_height, item['name'], 1)

            # Description
            x = self.pdf.get_x()
            self.pdf.multi_cell(col_widths[1], 10, item['description'], 1)
            self.pdf.set_xy(x + col_widths[1], y)

            # Unit Price
            self.pdf.cell(col_widths[2], row_height, f'PKR {item["unit_price"]:.2f}', 1, 0, align='L')

            # Quantity
            self.pdf.cell(col_widths[3], row_height, str(item['quantity']), 1, align='L')

            # Total
            self.pdf.cell(col_widths[4], row_height, f'PKR {total_item:.2f}', 1, align='L')

            self.pdf.ln(row_height)

        return col_widths

    def add_total(self):
        total_amount = sum(item['unit_price'] * item['quantity'] for item in self.items)
        self.pdf.ln(10)
        self.pdf.set_font("Arial", "B", size=12)
        self.pdf.cell(140, 10, txt="Total Amount:", border=1)
        self.pdf.cell(50, 10, txt=f"PKR {total_amount:.2f}", border=1)
        self.pdf.ln(55)  # Add some space before drawing the line
        
        self.pdf.set_font("Arial", "B", size=17)
        self.pdf.cell(0, 10, "Additional Notes", align='C', ln=True)

        # Draw a line
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(10)  # Add some space after the line

    def add_additional_notes(self):
        self.pdf.set_font('Arial', '', 12)
        self.pdf.multi_cell(0, 10, 'Thank you for your business!', 0, 1)

    def save_pdf(self, filename='invoice.pdf'):
        self.pdf.output(filename)

if __name__ == '__main__':
    company_info = {
        "name": "My Company",
        "address": "123 Main St, City, Country",
        "email": "info@mycompany.com",
        "phone": "+123456789"
    }
    client_info = {
        "name": "Client Name",
        "bill_to": "Client Name",
        "email": "client@email.com",
        "phone": "+987654321"
    }
    items = [
        {"name": "Item 1", "description": "Description 1", "unit_price": 100, "quantity": 2},
        {"name": "Item 2", "description": "Description 2", "unit_price": 50, "quantity": 3}
    ]
    invoice_info = {
        "invoice_number": "INV24",
        "date": "2024-06-21"
    }
    logo_path = "logo_resized.png"  # Path to the resized logo image

    invoice_generator = InvoiceGenerator(company_info, client_info, items, invoice_info, logo_path)
    invoice_generator.save_pdf()
