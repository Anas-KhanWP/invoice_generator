# admin_panel.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from functions.database import create_connection

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Admin Panel')
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(5)
        self.invoices_table.setHorizontalHeaderLabels(['Invoice Number', 'Client Name', 'Date', 'Total', 'File Path'])
        main_layout.addWidget(self.invoices_table)

        download_button = QPushButton('Download Selected Invoice')
        download_button.clicked.connect(self.download_invoice)
        main_layout.addWidget(download_button)

        self.setLayout(main_layout)
        self.load_invoices()

    def load_invoices(self):
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT invoice_number, client_name, date, total, file_path FROM invoices")
        rows = cur.fetchall()
        
        self.invoices_table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, data in enumerate(row):
                self.invoices_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    def download_invoice(self):
        selected_row = self.invoices_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, 'Selection Error', 'Please select an invoice to download.')
            return

        file_path = self.invoices_table.item(selected_row, 4).text()
        if not file_path:
            QMessageBox.warning(self, 'File Error', 'Selected invoice file path is invalid.')
            return

        save_path, _ = QFileDialog.getSaveFileName(self, 'Save Invoice PDF', 'invoice.pdf', 'PDF Files (*.pdf)')
        if save_path:
            try:
                with open(file_path, 'rb') as file:
                    content = file.read()
                with open(save_path, 'wb') as file:
                    file.write(content)
                QMessageBox.information(self, 'Download Success', f'Invoice downloaded successfully to:\n{save_path}')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred while downloading the invoice:\n{str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    admin_panel = AdminPanel()
    admin_panel.show()
    sys.exit(app.exec_())
