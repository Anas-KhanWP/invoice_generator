# main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QStyleFactory
from PyQt5.QtGui import QPalette, QColor
from functions.gui import InvoiceGUI
from functions.admin_panel import AdminPanel
from functions.database import create_table, drop_table, insert_invoice

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Invoice Generator Application')
        self.setGeometry(100, 100, 800, 600)
        
        # Apply custom styles
        self.apply_custom_styles()
        
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('Admin (Coming Soon)')

        generate_invoice_action = QAction('Generate Invoice', self)
        generate_invoice_action.triggered.connect(self.show_invoice_generator)
        file_menu.addAction(generate_invoice_action)

        admin_panel_action = QAction('Admin Panel', self)
        admin_panel_action.triggered.connect(self.show_admin_panel)
        file_menu.addAction(admin_panel_action)

        self.show_invoice_generator()

    def show_invoice_generator(self):
        self.invoice_gui = InvoiceGUI()
        self.setCentralWidget(self.invoice_gui)

    def show_admin_panel(self):
        self.admin_panel = AdminPanel()
        self.setCentralWidget(self.admin_panel)

    def apply_custom_styles(self):
        # Set custom palette colors
        palette = self.palette()

        # Set colors from heaviest to lightest
        palette.setColor(QPalette.Window, QColor("#2C3E50"))         # Main window background
        palette.setColor(QPalette.AlternateBase, QColor("#34495E"))  # Group box background
        palette.setColor(QPalette.Button, QColor("#E74C3C"))         # Button background
        palette.setColor(QPalette.ButtonText, QColor("#ECF0F1"))     # Button text color

        # Set text colors
        palette.setColor(QPalette.WindowText, QColor("#ECF0F1"))     # Text color for labels
        palette.setColor(QPalette.Text, QColor("#000"))           # Text color for input fields
        palette.setColor(QPalette.Base, QColor("#2C3E50"))           # Input fields background

        self.setPalette(palette)

        # Set font
        font = self.font()
        font.setPointSize(10)  # Set default font size for all widgets
        self.setFont(font)

        # Apply styles specifically to QMainWindow and its menu
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #000;
            }
            QMenuBar {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QMenuBar::item {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QMenuBar::item::selected {
                background-color: #E74C3C;
            }
            QMenu {
                background-color: #34495E;
                color: #ECF0F1;
            }
            QMenu::item::selected {
                background-color: #E74C3C;
            }
            QAction {
                color: #ECF0F1;
            }
        """)

if __name__ == '__main__':
    drop_table()  # Drop existing table to ensure new schema
    create_table()
    app = QApplication(sys.argv)

    # Apply Fusion style
    app.setStyle('Fusion')

    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
