import sqlite3, os, datetime

class LibraryDB:
    def __init__(self, path):
        self.path = path

    def _conn(self):
        conn = sqlite3.connect(self.path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        return conn

    def list_books_alpha(self, limit=500):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT BookID,book_number,title,author,isbn,copies FROM books ORDER BY LOWER(title) ASC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def search_books(self, q):
        conn = self._conn(); cur = conn.cursor()
        q = (q or "").strip()
        if not q:
            cur.execute("SELECT BookID,book_number,title,author,isbn,copies FROM books LIMIT 200")
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()
            return rows
        try:
            cur.execute("SELECT b.BookID,b.book_number,b.title,b.author,b.isbn,b.copies FROM books_fts f JOIN books b ON f.rowid=b.BookID WHERE books_fts MATCH ? LIMIT 200", (q+'*',))
            rows = [dict(r) for r in cur.fetchall()]
            if rows:
                conn.close()
                return rows
        except Exception:
            pass
        like_q = f"%{q}%"
        cur.execute("SELECT BookID,book_number,title,author,isbn,copies FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? LIMIT 200", (like_q,like_q,like_q))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def add_book(self, num, title, author, isbn, location, copies=1):
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO books(book_number,title,author,isbn,location,copies) VALUES(?,?,?,?,?,?)",
                        (num,title,author,isbn,location,copies))
            lid = cur.lastrowid
            try:
                cur.execute("INSERT INTO books_fts(rowid,title,author,isbn) VALUES(?,?,?,?)",(lid,title,author,isbn))
            except Exception:
                pass
            conn.commit()
            conn.close()
            return {"ok": True}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def add_member(self, num, name, cls):
        conn = self._conn(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO members(member_number,name,class) VALUES(?,?,?)", (num,name,cls))
            conn.commit(); conn.close()
            return {"ok": True}
        except Exception as e:
            conn.close(); return {"error": str(e)}

    def export_books(self):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT book_number,title,author,isbn,location,copies FROM books ORDER BY LOWER(title) ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def stats(self):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as total_books FROM books"); total_books = cur.fetchone()["total_books"]
        cur.execute("SELECT COUNT(*) as total_members FROM members"); total_members = cur.fetchone()["total_members"]
        cur.execute("SELECT COUNT(*) as active_loans FROM loans WHERE return_date IS NULL"); active_loans = cur.fetchone()["active_loans"]
        cur.execute("""SELECT b.title, COUNT(l.LoanID) as times
                       FROM books b
                       LEFT JOIN loans l ON l.book_id=b.BookID
                       GROUP BY b.BookID
                       ORDER BY times DESC
                       LIMIT 5""")
        top = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"total_books": total_books, "total_members": total_members, "active_loans": active_loans, "top": top}

    def loan_book(self, book_id, member_id, operator="system", due_days=14):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT copies, BookID FROM books WHERE BookID=?", (book_id,))
        b = cur.fetchone()
        if not b:
            conn.close()
            return {"error":"Βιβλίο δεν βρέθηκε"}
        cur.execute("SELECT COUNT(*) as active_loans FROM loans WHERE book_id=? AND return_date IS NULL", (book_id,))
        active = cur.fetchone()["active_loans"]
        if active >= b["copies"]:
            conn.close()
            return {"error":"Όλα τα αντίτυπα του βιβλίου είναι δανεισμένα"}

        loan_date = datetime.datetime.now()
        due_date = loan_date + datetime.timedelta(days=due_days)
        cur.execute("INSERT INTO loans(book_id,member_id,loan_date,due_date,operator) VALUES(?,?,?,?,?)",
                    (book_id, member_id, loan_date, due_date, operator))
        conn.commit()
        conn.close()
        return {"ok": True, "due_date": due_date.strftime("%Y-%m-%d")}

    def return_book(self, loan_id):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("SELECT return_date FROM loans WHERE LoanID=?", (loan_id,))
        r = cur.fetchone()
        if not r:
            conn.close()
            return {"error":"Δάνειο δεν βρέθηκε"}
        if r["return_date"] is not None:
            conn.close()
            return {"error":"Το βιβλίο έχει ήδη επιστραφεί"}
        cur.execute("UPDATE loans SET return_date=? WHERE LoanID=?", (datetime.datetime.now(), loan_id))
        conn.commit()
        conn.close()
        return {"ok": True}

    def list_active_loans(self):
        conn = self._conn(); cur = conn.cursor()
        cur.execute("""SELECT l.LoanID, m.name as member_name, b.title as book_title, l.loan_date, l.due_date
                       FROM loans l
                       JOIN members m ON l.member_id=m.MemberID
                       JOIN books b ON l.book_id=b.BookID
                       WHERE l.return_date IS NULL
                       ORDER BY l.due_date ASC""")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
