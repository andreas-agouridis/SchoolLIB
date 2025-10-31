import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "library.db")

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Δημιουργία βασικών tables
cur.execute("""CREATE TABLE IF NOT EXISTS books (
    BookID INTEGER PRIMARY KEY AUTOINCREMENT,
    book_number TEXT UNIQUE,
    title TEXT,
    author TEXT,
    isbn TEXT,
    location TEXT,
    copies INTEGER DEFAULT 1
)""")

cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(title,author,isbn)""")

cur.execute("""CREATE TABLE IF NOT EXISTS members (
    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    member_number TEXT UNIQUE,
    name TEXT,
    class TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS loans (
    LoanID INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    member_id INTEGER,
    loan_date TIMESTAMP,
    due_date TIMESTAMP,
    return_date TIMESTAMP,
    operator TEXT
)""")

conn.commit(); conn.close()
print("New library.db created successfully!")
