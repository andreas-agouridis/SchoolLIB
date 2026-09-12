import sqlite3
import datetime
import os


def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def today_str():
    return datetime.date.today().isoformat()


class LibraryDB:
    def __init__(self, path):
        self.path = path
        self._init_schema()

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS libraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT NULL
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS shelves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
            parent_id INTEGER REFERENCES shelves(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 0
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
            book_number TEXT,
            title TEXT NOT NULL,
            author TEXT,
            publisher TEXT,
            edition TEXT,
            year TEXT,
            pages INTEGER,
            isbn TEXT,
            dewey TEXT,
            copies INTEGER DEFAULT 1,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS book_categories (
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
            PRIMARY KEY (book_id, category_id)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS book_tags (
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            tag TEXT NOT NULL,
            PRIMARY KEY (book_id, tag)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS book_shelves (
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            shelf_id INTEGER NOT NULL REFERENCES shelves(id) ON DELETE CASCADE,
            PRIMARY KEY (book_id, shelf_id)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
            member_number TEXT,
            name TEXT NOT NULL,
            class TEXT,
            email TEXT,
            phone TEXT,
            notes TEXT,
            created_at TEXT,
            updated_at TEXT
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            library_id INTEGER NOT NULL REFERENCES libraries(id) ON DELETE CASCADE,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
            member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
            loan_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            operator TEXT,
            renewals INTEGER DEFAULT 0,
            notes TEXT
        )""")
        cur.execute("CREATE TABLE IF NOT EXISTS app_settings (key TEXT PRIMARY KEY, value TEXT)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_books_author ON books(author)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_members_name ON members(name)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_loans_active ON loans(return_date)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_loans_member ON loans(member_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_loans_book ON loans(book_id)")

        try:
            cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS books_fts USING fts5(title, author, isbn)")
        except Exception:
            pass

        if not cur.execute("SELECT COUNT(*) FROM libraries").fetchone()[0]:
            cur.execute("INSERT INTO libraries(name, created_at) VALUES(?,?)", ("Κεντρική Βιβλιοθήκη", now_str()))

        for key in ("due_days", "max_loans", "remind_days", "font_size", "school_name",
                    "auto_backup", "backup_password", "backup_count"):
            cur.execute("INSERT OR IGNORE INTO app_settings(key, value) VALUES(?,?)", (key, ""))

        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        conn = self._conn()
        row = conn.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        conn.close()
        if row is None:
            return default
        return row["value"] or default

    def restore_from(self, src_path):
        import shutil
        conn = self._conn()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.close()
        shutil.copy2(src_path, self.path)
        self._init_schema()

    def set_setting(self, key, value):
        conn = self._conn()
        conn.execute("INSERT INTO app_settings(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                     (key, value))
        conn.commit()
        conn.close()

    def wipe_for_test(self):
        conn = self._conn()
        for t in ("book_categories", "book_tags", "book_shelves", "books_fts",
                  "loans", "books", "members", "shelves", "categories"):
            try:
                conn.execute(f"DELETE FROM {t}")
            except Exception:
                pass
        conn.commit()
        conn.close()

    # ---- Libraries --------------------------------------------
    def list_libraries(self):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute("SELECT id, name FROM libraries ORDER BY name").fetchall()]
        conn.close()
        return rows

    def get_library_name(self, library_id):
        conn = self._conn()
        row = conn.execute("SELECT name FROM libraries WHERE id=?", (library_id,)).fetchone()
        conn.close()
        return row["name"] if row else ""

    def add_library(self, name):
        conn = self._conn()
        try:
            conn.execute("INSERT INTO libraries(name, created_at) VALUES(?,?)", (name, now_str()))
            conn.commit()
            lid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            conn.close()
            return {"ok": True, "id": lid}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def delete_library(self, library_id):
        conn = self._conn()
        libs = self.list_libraries()
        if len(libs) <= 1 and library_id in [l["id"] for l in libs]:
            conn.close()
            return {"error": "Δεν μπορείτε να διαγράψετε την τελευταία βιβλιοθήκη"}
        try:
            conn.execute("DELETE FROM libraries WHERE id=?", (library_id,))
            conn.commit()
            conn.close()
            return {"ok": True}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def rename_library(self, library_id, name):
        conn = self._conn()
        try:
            conn.execute("UPDATE libraries SET name=? WHERE id=?", (name, library_id))
            conn.commit()
            conn.close()
            return {"ok": True}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    # ---- Shelves (hierarchical) -------------------------------
    def add_shelf(self, name, parent_id=None, library_id=None):
        conn = self._conn()
        if library_id is None:
            row = conn.execute("SELECT id FROM libraries ORDER BY id LIMIT 1").fetchone()
            library_id = row["id"] if row else 1
        level = 0
        if parent_id:
            prow = conn.execute("SELECT level FROM shelves WHERE id=?", (parent_id,)).fetchone()
            level = (prow["level"] + 1) if prow else 0
        cur = conn.cursor()
        cur.execute("INSERT INTO shelves(library_id, parent_id, name, level) VALUES(?,?,?,?)",
                    (library_id, parent_id, name, level))
        sid = cur.lastrowid
        conn.commit()
        conn.close()
        return sid

    def list_shelves(self, library_id=None):
        conn = self._conn()
        if library_id:
            rows = [dict(r) for r in conn.execute(
                "SELECT id, library_id, parent_id, name, level FROM shelves WHERE library_id=? ORDER BY name",
                (library_id,)).fetchall()]
        else:
            rows = [dict(r) for r in conn.execute(
                "SELECT id, library_id, parent_id, name, level FROM shelves ORDER BY name").fetchall()]
        conn.close()
        return rows

    def child_shelves(self, parent_id):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT id, parent_id, name FROM shelves WHERE parent_id=? ORDER BY name", (parent_id,)).fetchall()]
        conn.close()
        return rows

    def rename_shelf(self, shelf_id, name):
        conn = self._conn()
        conn.execute("UPDATE shelves SET name=? WHERE id=?", (name, shelf_id))
        conn.commit()
        conn.close()

    def move_shelf(self, shelf_id, new_parent_id):
        conn = self._conn()
        parent = None
        if new_parent_id:
            parent = conn.execute("SELECT level FROM shelves WHERE id=?", (new_parent_id,)).fetchone()
        level = parent["level"] + 1 if parent else 0
        conn.execute("UPDATE shelves SET parent_id=?, level=? WHERE id=?", (new_parent_id, level, shelf_id))
        conn.commit()
        conn.close()

    def delete_shelf(self, shelf_id):
        conn = self._conn()
        conn.execute("DELETE FROM book_shelves WHERE shelf_id=?", (shelf_id,))
        conn.execute("DELETE FROM shelves WHERE id=? OR parent_id=?", (shelf_id, shelf_id))
        conn.commit()
        conn.close()

    def shelf_books_count(self, shelf_id):
        conn = self._conn()
        row = conn.execute("SELECT COUNT(*) FROM book_shelves WHERE shelf_id=?", (shelf_id,)).fetchone()
        conn.close()
        return row[0]

    def assign_books_to_shelf(self, book_ids, shelf_id):
        conn = self._conn()
        for bid in book_ids:
            conn.execute("INSERT OR REPLACE INTO book_shelves(book_id, shelf_id) VALUES(?,?)", (bid, shelf_id))
        conn.commit()
        conn.close()

    def remove_book_from_shelf(self, book_id, shelf_id):
        conn = self._conn()
        conn.execute("DELETE FROM book_shelves WHERE book_id=? AND shelf_id=?", (book_id, shelf_id))
        conn.commit()
        conn.close()

    # ---- Categories --------------------------------------------
    def list_categories(self):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT c.id, c.name, COUNT(bc.book_id) as cnt FROM categories c "
            "LEFT JOIN book_categories bc ON bc.category_id=c.id "
            "GROUP BY c.id ORDER BY c.name").fetchall()]
        conn.close()
        return rows

    def add_category(self, name):
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO categories(name) VALUES(?)", (name,))
            cid = cur.lastrowid
            conn.commit()
            conn.close()
            return {"ok": True, "id": cid}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def rename_category(self, category_id, name):
        conn = self._conn()
        try:
            conn.execute("UPDATE categories SET name=? WHERE id=?", (name, category_id))
            conn.commit()
            conn.close()
            return {"ok": True}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def delete_category(self, category_id):
        conn = self._conn()
        conn.execute("DELETE FROM book_categories WHERE category_id=?", (category_id,))
        conn.execute("DELETE FROM categories WHERE id=?", (category_id,))
        conn.commit()
        conn.close()

    def set_book_categories(self, book_id, category_ids):
        conn = self._conn()
        conn.execute("DELETE FROM book_categories WHERE book_id=?", (book_id,))
        for cid in category_ids:
            conn.execute("INSERT INTO book_categories(book_id, category_id) VALUES(?,?)", (book_id, cid))
        conn.commit()
        conn.close()

    # ---- Tags ---------------------------------------------------
    def list_common_tags(self, limit=100):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT tag, COUNT(*) as cnt FROM book_tags GROUP BY tag ORDER BY cnt DESC LIMIT ?",
            (limit,)).fetchall()]
        conn.close()
        return rows

    def set_book_tags(self, book_id, tags):
        conn = self._conn()
        conn.execute("DELETE FROM book_tags WHERE book_id=?", (book_id,))
        for t in tags:
            t = t.strip()
            if t:
                conn.execute("INSERT OR IGNORE INTO book_tags(book_id, tag) VALUES(?,?)", (book_id, t))
        conn.commit()
        conn.close()

    # ---- Books ---------------------------------------------------
    def _book_full(self, row, conn):
        b = dict(row)
        b["categories"] = [r["name"] for r in conn.execute(
            "SELECT c.name FROM book_categories bc JOIN categories c ON c.id=bc.category_id WHERE bc.book_id=? ORDER BY c.name",
            (b["id"],)).fetchall()]
        b["tags"] = [r["tag"] for r in conn.execute(
            "SELECT tag FROM book_tags WHERE book_id=? ORDER BY tag", (b["id"],)).fetchall()]
        b["shelves"] = [r["name"] for r in conn.execute(
            "SELECT s.name FROM book_shelves bs JOIN shelves s ON s.id=bs.shelf_id WHERE bs.book_id=? ORDER BY s.name",
            (b["id"],)).fetchall()]
        b["available"] = b["copies"] - self._active_loans_count(conn, b["id"])
        return b

    def _active_loans_count(self, conn, book_id):
        row = conn.execute("SELECT COUNT(*) FROM loans WHERE book_id=? AND return_date IS NULL",
                           (book_id,)).fetchone()
        return row[0]

    def get_book(self, book_id):
        conn = self._conn()
        row = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not row:
            conn.close()
            return None
        b = self._book_full(row, conn)
        conn.close()
        return b

    def _fts_update(self, conn, book_id, title, author, isbn):
        try:
            conn.execute("DELETE FROM books_fts WHERE rowid=?", (book_id,))
            conn.execute("INSERT INTO books_fts(rowid, title, author, isbn) VALUES(?,?,?,?)",
                         (book_id, title, author or "", isbn or ""))
        except Exception:
            pass

    def add_book(self, data):
        conn = self._conn()
        try:
            columns = ["library_id", "book_number", "title", "author", "publisher", "edition",
                       "year", "pages", "isbn", "dewey", "copies", "notes"]
            vals = {k: data.get(k) for k in columns}
            if not vals.get("library_id"):
                row = conn.execute("SELECT id FROM libraries ORDER BY id LIMIT 1").fetchone()
                vals["library_id"] = row["id"] if row else 1
            if not vals.get("title"):
                conn.close()
                return {"error": "Ο τίτλος είναι υποχρεωτικός"}
            vals["copies"] = int(vals.get("copies") or 1) or 1
            vals["created_at"] = now_str()
            vals["updated_at"] = now_str()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO books(library_id, book_number, title, author, publisher, edition, year, pages, isbn, dewey, copies, notes, created_at, updated_at) "
                "VALUES(:library_id,:book_number,:title,:author,:publisher,:edition,:year,:pages,:isbn,:dewey,:copies,:notes,:created_at,:updated_at)",
                vals)
            bid = cur.lastrowid
            self._fts_update(conn, bid, vals["title"], vals["author"], vals["isbn"])
            conn.commit()
            conn.close()
            if data.get("categories"):
                self.set_book_categories(bid, [int(x) for x in data["categories"]])
            if data.get("tags"):
                self.set_book_tags(bid, data["tags"])
            if data.get("shelves"):
                c2 = self._conn()
                for sid in data["shelves"]:
                    c2.execute("INSERT OR IGNORE INTO book_shelves(book_id, shelf_id) VALUES(?,?)",
                               (bid, int(sid)))
                c2.commit()
                c2.close()
            return {"ok": True, "id": bid}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def update_book(self, book_id, data):
        conn = self._conn()
        fields = ["book_number", "title", "author", "publisher", "edition", "year", "pages",
                  "isbn", "dewey", "copies", "notes"]
        sets = []
        vals = {}
        for f in fields:
            if f in data:
                sets.append(f"{f}=:_{f}")
                vals[f"_{f}"] = data[f]
        sets.append("updated_at=:updated_at")
        vals["updated_at"] = now_str()
        vals["id"] = book_id
        if sets:
            conn.execute(f"UPDATE books SET {', '.join(sets)} WHERE id=:id", vals)
        conn.commit()
        if "title" in data or "author" in data or "isbn" in data:
            row = conn.execute("SELECT title, author, isbn FROM books WHERE id=?",
                               (book_id,)).fetchone()
            if row:
                self._fts_update(conn, book_id, row["title"], row["author"], row["isbn"])
        conn.close()
        if data.get("categories") is not None:
            self.set_book_categories(book_id, [int(x) for x in data["categories"]])
        if data.get("tags") is not None:
            self.set_book_tags(book_id, data["tags"])
        if data.get("shelves") is not None:
            c2 = self._conn()
            c2.execute("DELETE FROM book_shelves WHERE book_id=?", (book_id,))
            for sid in data["shelves"]:
                c2.execute("INSERT OR IGNORE INTO book_shelves(book_id, shelf_id) VALUES(?,?)",
                           (book_id, int(sid)))
            c2.commit()
            c2.close()
        return {"ok": True}

    def delete_book(self, book_id):
        conn = self._conn()
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        conn.close()
        return {"ok": True}

    def search_books(self, q, library_id=None, category_id=None, shelf_id=None, tag=None, limit=500):
        conn = self._conn()
        conditions = []
        params = []
        if q and q.strip():
            qq = q.strip()
            try:
                like = f"%{qq}%"
                rows = conn.execute(
                    "SELECT b.* FROM books_fts f JOIN books b ON b.id=f.rowid WHERE books_fts MATCH ? LIMIT ?",
                    (qq.replace('"', ' ') + '*', limit)).fetchall()
                if rows:
                    books = [self._book_full(r, conn) for r in rows]
                    conn.close()
                    return books
            except Exception:
                pass
        if not q:
            conditions.append("1=1")
        else:
            like = f"%{q.strip()}%"
            conditions.append("(title LIKE ? OR author LIKE ? OR isbn LIKE ? OR book_number LIKE ?)")
            params.extend([like, like, like, like])
        if library_id:
            conditions.append("library_id=?")
            params.append(library_id)
        if category_id:
            conditions.append("id IN (SELECT book_id FROM book_categories WHERE category_id=?)")
            params.append(category_id)
        if shelf_id:
            conditions.append("id IN (SELECT book_id FROM book_shelves WHERE shelf_id=?)")
            params.append(shelf_id)
        if tag:
            conditions.append("id IN (SELECT book_id FROM book_tags WHERE tag=?)")
            params.append(tag)
        params.append(limit)
        sql = (f"SELECT * FROM books WHERE {' AND '.join(conditions)} "
               f"ORDER BY LOWER(title), LOWER(author) LIMIT ?")
        rows = conn.execute(sql, params).fetchall()
        books = [self._book_full(r, conn) for r in rows]
        conn.close()
        return books

    def latest_books(self, limit=10):
        conn = self._conn()
        rows = conn.execute("SELECT * FROM books ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        books = [self._book_full(r, conn) for r in rows]
        conn.close()
        return books

    def find_duplicate(self, title, isbn, exclude_id=None):
        conn = self._conn()
        params = []
        conds = []
        if title:
            conds.append("LOWER(title)=LOWER(?)")
            params.append(title.strip())
        if isbn:
            conds.append("isbn=?")
            params.append(isbn.strip())
        if exclude_id:
            conds.append("id!=?")
            params.append(exclude_id)
        if not conds:
            conn.close()
            return None
        sql = f"SELECT * FROM books WHERE {' OR '.join(conds)} LIMIT 1"
        row = conn.execute(sql, params).fetchone()
        book = self._book_full(row, conn) if row else None
        conn.close()
        return book

    def delete_all_books(self):
        conn = self._conn()
        conn.execute("DELETE FROM books")
        conn.execute("DELETE FROM books_fts")
        conn.commit()
        conn.close()

    # ---- Members --------------------------------------------------
    def add_member(self, data):
        conn = self._conn()
        try:
            if not data.get("name"):
                conn.close()
                return {"error": "Το όνομα είναι υποχρεωτικό"}
            if not data.get("library_id"):
                row = conn.execute("SELECT id FROM libraries ORDER BY id LIMIT 1").fetchone()
                data["library_id"] = row["id"] if row else 1
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO members(library_id, member_number, name, class, email, phone, notes, created_at, updated_at) "
                "VALUES(:library_id,:member_number,:name,:class,:email,:phone,:notes,:created_at,:updated_at)",
                {"library_id": data.get("library_id"), "member_number": data.get("member_number"),
                 "name": data.get("name"), "class": data.get("class"), "email": data.get("email"),
                 "phone": data.get("phone"), "notes": data.get("notes"),
                 "created_at": now_str(), "updated_at": now_str()})
            mid = cur.lastrowid
            conn.commit()
            conn.close()
            return {"ok": True, "id": mid}
        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def update_member(self, member_id, data):
        conn = self._conn()
        fields = ["member_number", "name", "class", "email", "phone", "notes"]
        sets = []
        vals = {"updated_at": now_str(), "id": member_id}
        for f in fields:
            if f in data:
                sets.append(f"{f}=:_{f}")
                vals[f"_{f}"] = data[f]
        sets.append("updated_at=:updated_at")
        conn.execute(f"UPDATE members SET {', '.join(sets)} WHERE id=:id", vals)
        conn.commit()
        conn.close()
        return {"ok": True}

    def delete_member(self, member_id):
        conn = self._conn()
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
        conn.commit()
        conn.close()

    def get_member(self, member_id):
        conn = self._conn()
        row = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def list_members(self, q=None, class_name=None, library_id=None):
        conn = self._conn()
        conds = []
        params = []
        if q and q.strip():
            like = f"%{q.strip()}%"
            conds.append("(name LIKE ? OR member_number LIKE ?)")
            params.extend([like, like])
        if class_name:
            conds.append("class=?")
            params.append(class_name)
        if library_id:
            conds.append("library_id=?")
            params.append(library_id)
        where = f"WHERE {' AND '.join(conds)}" if conds else ""
        params.append(2500)
        rows = conn.execute(f"SELECT * FROM members {where} ORDER BY LOWER(name) LIMIT ?", params).fetchall()
        out = []
        for r in rows:
            m = dict(r)
            m["active_loans"] = conn.execute(
                "SELECT COUNT(*) FROM loans WHERE member_id=? AND return_date IS NULL", (m["id"],)).fetchone()[0]
            out.append(m)
        conn.close()
        return out

    def member_classes(self):
        conn = self._conn()
        rows = [r["class"] for r in conn.execute(
            "SELECT DISTINCT class FROM members WHERE class IS NOT NULL AND class!='' ORDER BY class").fetchall()]
        conn.close()
        return rows

    # ---- Loans -----------------------------------------------------
    def loan_book(self, book_id, member_id, due_days=14, operator=""):
        conn = self._conn()
        book = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            conn.close()
            return {"error": "Το βιβλίο δεν βρέθηκε"}
        active = conn.execute("SELECT COUNT(*) FROM loans WHERE book_id=? AND return_date IS NULL",
                              (book_id,)).fetchone()[0]
        if active >= book["copies"]:
            conn.close()
            return {"error": "Όλα τα αντίτυπα είναι ήδη δανεισμένα"}
        member = conn.execute("SELECT id FROM members WHERE id=?", (member_id,)).fetchone()
        if not member:
            conn.close()
            return {"error": "Το μέλος δεν βρέθηκε"}
        loan_date = datetime.date.today()
        due_date = loan_date + datetime.timedelta(days=int(due_days or 14))
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO loans(library_id, book_id, member_id, loan_date, due_date, operator, renewals) "
            "VALUES(?,?,?,?,?,?,0)",
            (book["library_id"], book_id, member_id, loan_date.isoformat(), due_date.isoformat(), operator))
        conn.commit()
        conn.close()
        return {"ok": True, "due_date": due_date.isoformat()}

    def add_loan_record(self, book_id, member_id, loan_date, due_date, return_date=None,
                        renewals=0, operator=""):
        conn = self._conn()
        book = conn.execute("SELECT library_id FROM books WHERE id=?", (book_id,)).fetchone()
        if not book:
            conn.close()
            return {"error": "Το βιβλίο δεν βρέθηκε"}
        conn.execute(
            "INSERT INTO loans(library_id, book_id, member_id, loan_date, due_date, return_date, "
            "operator, renewals) VALUES(?,?,?,?,?,?,?,?)",
            (book["library_id"], book_id, member_id, loan_date.isoformat(), due_date.isoformat(),
             return_date.isoformat() if return_date else None, operator, int(renewals or 0)))
        conn.commit()
        conn.close()
        return {"ok": True}

    def return_book(self, loan_id, return_date=None):
        conn = self._conn()
        row = conn.execute("SELECT return_date FROM loans WHERE id=?", (loan_id,)).fetchone()
        if not row:
            conn.close()
            return {"error": "Το δάνειο δεν βρέθηκε"}
        if row["return_date"]:
            conn.close()
            return {"error": "Το βιβλίο έχει ήδη επιστραφεί"}
        conn.execute("UPDATE loans SET return_date=? WHERE id=?",
                     (return_date or datetime.date.today().isoformat(), loan_id))
        conn.commit()
        conn.close()
        return {"ok": True}

    def renew_loan(self, loan_id, extra_days=7):
        conn = self._conn()
        row = conn.execute("SELECT due_date, renewals FROM loans WHERE id=? AND return_date IS NULL",
                           (loan_id,)).fetchone()
        if not row:
            conn.close()
            return {"error": "Δεν βρέθηκε ενεργό δάνειο"}
        new_due = datetime.date.fromisoformat(row["due_date"]) + datetime.timedelta(days=int(extra_days or 7))
        conn.execute("UPDATE loans SET due_date=?, renewals=renewals+1 WHERE id=?",
                     (new_due.isoformat(), loan_id))
        conn.commit()
        conn.close()
        return {"ok": True, "due_date": new_due.isoformat()}

    def get_loan(self, loan_id):
        conn = self._conn()
        row = conn.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def active_loans(self, q=None):
        conn = self._conn()
        conds = ["l.return_date IS NULL"]
        params = []
        if q and q.strip():
            like = f"%{q.strip()}%"
            conds.append("(b.title LIKE ? OR m.name LIKE ?)")
            params.extend([like, like])
        params.append(5000)
        rows = conn.execute(
            "SELECT l.id, l.library_id, l.book_id, l.member_id, l.loan_date, l.due_date, l.renewals, l.notes, "
            "b.title as book_title, b.book_number, m.name as member_name, m.member_number "
            "FROM loans l JOIN books b ON b.id=l.book_id JOIN members m ON m.id=l.member_id "
            f"WHERE {' AND '.join(conds)} ORDER BY l.due_date LIMIT ?", params).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            today = datetime.date.today()
            due = datetime.date.fromisoformat(d["due_date"][:10])
            d["days_left"] = (due - today).days
            out.append(d)
        conn.close()
        return out

    def overdue_loans(self):
        return [l for l in self.active_loans() if l["days_left"] < 0]

    def upcoming_loans(self, days=3):
        today = datetime.date.today()
        return [l for l in self.active_loans() if 0 <= l["days_left"] <= days]

    def member_active_loans(self, member_id):
        conn = self._conn()
        rows = conn.execute(
            "SELECT l.id, b.title, l.loan_date, l.due_date FROM loans l JOIN books b ON b.id=l.book_id "
            "WHERE l.member_id=? AND l.return_date IS NULL ORDER BY l.due_date", (member_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def book_loan_history(self, book_id):
        conn = self._conn()
        rows = conn.execute(
            "SELECT l.loan_date, l.due_date, l.return_date, m.name as member_name FROM loans l "
            "JOIN members m ON m.id=l.member_id WHERE l.book_id=? ORDER BY l.loan_date DESC",
            (book_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def loan_history(self, q=None, member_id=None, book_id=None, date_from=None, date_to=None,
                     returned=None, limit=2500):
        conn = self._conn()
        conds = ["1=1"]
        params = []
        if q and q.strip():
            like = f"%{q.strip()}%"
            conds.append("(b.title LIKE ? OR m.name LIKE ?)")
            params.extend([like, like])
        if member_id:
            conds.append("l.member_id=?")
            params.append(member_id)
        if book_id:
            conds.append("l.book_id=?")
            params.append(book_id)
        if date_from:
            conds.append("l.loan_date>=?")
            params.append(date_from)
        if date_to:
            conds.append("l.loan_date<=?")
            params.append(date_to)
        if returned is True:
            conds.append("l.return_date IS NOT NULL")
        elif returned is False:
            conds.append("l.return_date IS NULL")
        params.append(limit)
        rows = conn.execute(
            "SELECT l.id, b.title as book_title, b.book_number, m.name as member_name, m.member_number, "
            "l.loan_date, l.due_date, l.return_date, l.renewals, l.operator "
            "FROM loans l JOIN books b ON b.id=l.book_id JOIN members m ON m.id=l.member_id "
            f"WHERE {' AND '.join(conds)} ORDER BY l.loan_date DESC LIMIT ?", params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def loan_stats(self):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT l.loan_date AS date, COUNT(*) as cnt FROM loans l GROUP BY l.loan_date ORDER BY l.loan_date ASC").fetchall()]
        conn.close()
        return rows

    def delete_loan(self, loan_id):
        conn = self._conn()
        conn.execute("DELETE FROM loans WHERE id=?", (loan_id,))
        conn.commit()
        conn.close()

    # ---- Statistics ------------------------------------------------
    def stats(self):
        conn = self._conn()
        s = {}
        s["books"] = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        s["copies"] = conn.execute("SELECT COALESCE(SUM(copies),0) FROM books").fetchone()[0]
        s["members"] = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        s["libraries"] = conn.execute("SELECT COUNT(*) FROM libraries").fetchone()[0]
        s["shelves"] = conn.execute("SELECT COUNT(*) FROM shelves").fetchone()[0]
        s["categories"] = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        s["active_loans"] = conn.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL").fetchone()[0]
        s["overdue"] = conn.execute(
            "SELECT COUNT(*) FROM loans WHERE return_date IS NULL AND due_date<DATE('now')").fetchone()[0]
        s["due_soon"] = conn.execute(
            "SELECT COUNT(*) FROM loans WHERE return_date IS NULL AND due_date>=DATE('now') AND due_date<=DATE('now','+3 day')").fetchone()[0]
        s["loans_total"] = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
        conn.close()
        return s

    def top_books(self, limit=10):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT b.title, b.author, COUNT(l.id) as times FROM books b "
            "LEFT JOIN loans l ON l.book_id=b.id "
            "GROUP BY b.id ORDER BY times DESC, b.title LIMIT ?", (limit,)).fetchall()]
        conn.close()
        return rows

    def categories_distribution(self):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT c.name, COUNT(bc.book_id) as cnt FROM categories c "
            "LEFT JOIN book_categories bc ON bc.category_id=c.id "
            "GROUP BY c.id ORDER BY cnt DESC LIMIT 12").fetchall()]
        conn.close()
        return rows

    def loans_per_month(self, months=6):
        conn = self._conn()
        cutoff = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        for _ in range(months - 1):
            cutoff = (cutoff - datetime.timedelta(days=1)).replace(day=1)
        cutoff_s = cutoff.isoformat()
        rows = [dict(r) for r in conn.execute(
            "SELECT substr(loan_date,1,7) as month, COUNT(*) as cnt FROM loans "
            "WHERE loan_date>=? GROUP BY month ORDER BY month", (cutoff_s,)).fetchall()]
        conn.close()
        return rows

    def export_all_books(self):
        conn = self._conn()
        rows = [dict(r) for r in conn.execute(
            "SELECT b.*, l.name as library_name FROM books b "
            "LEFT JOIN libraries l ON l.id=b.library_id ORDER BY LOWER(b.title)").fetchall()]
        out = []
        for r in rows:
            b = self._book_full(dict(r), conn)
            out.append(b)
        conn.close()
        return out