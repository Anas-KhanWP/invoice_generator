# database.py
import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('invoices.db')
        return conn
    except Error as e:
        print(e)
    return conn

def create_table():
    """Create the invoices table."""
    conn = create_connection()
    if conn is not None:
        try:
            sql_create_invoices_table = """CREATE TABLE IF NOT EXISTS invoices (
                                                id INTEGER PRIMARY KEY,
                                                client_name TEXT NOT NULL,
                                                client_phone TEXT,
                                                client_email TEXT,
                                                bill_to TEXT,
                                                items TEXT,
                                                invoice_number TEXT UNIQUE,
                                                date TEXT,
                                                total REAL,
                                                file_path TEXT
                                            );"""
            conn.execute(sql_create_invoices_table)
            conn.commit()
        except Error as e:
            print(e)
    else:
        print("Error! Cannot create the database connection.")

def insert_invoice(client_name, client_phone, client_email, bill_to, items, invoice_number, date, total, file_path):
    """Insert a new invoice into the invoices table."""
    conn = create_connection()
    sql = ''' INSERT INTO invoices(client_name, client_phone, client_email, bill_to, items, invoice_number, date, total, file_path)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (client_name, client_phone, client_email, bill_to, items, invoice_number, date, total, file_path))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")
        return None

def get_invoice_by_number(invoice_number):
    """Retrieve an invoice from the database by its invoice number."""
    conn = create_connection()
    sql = "SELECT * FROM invoices WHERE invoice_number = ?"
    cur = conn.cursor()
    cur.execute(sql, (invoice_number,))
    row = cur.fetchone()
    return row

def update_invoice_file_path(invoice_number, file_path):
    """Update the file_path of an invoice."""
    conn = create_connection()
    sql = "UPDATE invoices SET file_path = ? WHERE invoice_number = ?"
    cur = conn.cursor()
    cur.execute(sql, (file_path, invoice_number))
    conn.commit()

def drop_table():
    """Drop the invoices table if it exists."""
    conn = create_connection()
    try:
        sql_drop_invoices_table = "DROP TABLE IF EXISTS invoices"
        conn.execute(sql_drop_invoices_table)
        conn.commit()
    except Error as e:
        print(e)