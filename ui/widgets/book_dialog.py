from PySide6 import QtCore, QtWidgets

from services import isbn_lookup


class IsbnWorker(QtCore.QObject):
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)

    def start(self, isbn):
        import threading

        def work():
            try:
                result = isbn_lookup.lookup_isbn(isbn)
                self.finished.emit(result)
            except Exception as e:
                self.failed.emit(str(e))

        t = threading.Thread(target=work, daemon=True)
        t.start()

        def watchdog():
            t.join(timeout=30)
            if t.is_alive():
                self.failed.emit("Χρονικό όριο (timeout) — η αναζήτηση άργησε να απαντήσει.")

        threading.Thread(target=watchdog, daemon=True).start()


class BookDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None, book=None):
        super().__init__(parent)
        self.db = db
        self.book = book
        self.setWindowTitle("Επεξεργασία Βιβλίου" if book else "Προσθήκη Βιβλίου")
        self.resize(560, 640)
        self._worker = None
        self._build()
        if book:
            self._load_book(book)

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        form.setSpacing(10)
        self.ed_number = QtWidgets.QLineEdit()
        form.addRow("Αριθμός βιβλίου:", self.ed_number)

        self.ed_isbn = QtWidgets.QLineEdit()
        isbn_row = QtWidgets.QWidget()
        hl = QtWidgets.QHBoxLayout(isbn_row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self.ed_isbn, 1)
        self.btn_isbn = QtWidgets.QPushButton("Αυτόματη συμπλήρωση από ISBN")
        self.btn_isbn.setObjectName("secondary")
        self.btn_isbn.clicked.connect(self._lookup_isbn)
        hl.addWidget(self.btn_isbn)
        form.addRow("ISBN:", isbn_row)

        self.ed_title = QtWidgets.QLineEdit()
        form.addRow("Τίτλος *:", self.ed_title)
        self.ed_author = QtWidgets.QLineEdit()
        form.addRow("Συγγραφέας:", self.ed_author)
        self.ed_publisher = QtWidgets.QLineEdit()
        form.addRow("Εκδότης:", self.ed_publisher)

        row2 = QtWidgets.QHBoxLayout()
        self.ed_edition = QtWidgets.QLineEdit()
        row2.addWidget(self.ed_edition)
        self.ed_year = QtWidgets.QLineEdit()
        row2.addWidget(self.ed_year)
        self.sp_pages = QtWidgets.QSpinBox(); self.sp_pages.setRange(0, 100000)
        row2.addWidget(self.sp_pages)
        self.sp_copies = QtWidgets.QSpinBox(); self.sp_copies.setRange(1, 10000); self.sp_copies.setValue(1)
        row2.addWidget(self.sp_copies)
        form.addRow("Έκδοση / Έτος / Σελίδες / Αντίτυπα:", row2)

        self.ed_dewey = QtWidgets.QLineEdit()
        form.addRow("Ταξιθετικός (Dewey):", self.ed_dewey)

        self.cat_list = QtWidgets.QListWidget()
        self.cat_list.setMaximumHeight(120)
        self.ed_new_cat = QtWidgets.QLineEdit()
        self.ed_new_cat.setPlaceholderText("Νέα κατηγορία + Enter")
        self.ed_new_cat.returnPressed.connect(self._add_new_cat)
        form.addRow("Κατηγορίες:", self.cat_list)
        form.addRow("", self.ed_new_cat)

        self.ed_tags = QtWidgets.QLineEdit()
        self.ed_tags.setPlaceholderText("π.χ. ελληνική λογοτεχνία, μυθιστόρημα")
        form.addRow("Ετικέτες (κόμμα):", self.ed_tags)

        self.shelf_list = QtWidgets.QListWidget()
        self.shelf_list.setMaximumHeight(100)
        form.addRow("Ράφια:", self.shelf_list)

        self.ed_notes = QtWidgets.QTextEdit()
        self.ed_notes.setMaximumHeight(70)
        form.addRow("Σημειώσεις:", self.ed_notes)

        layout.addLayout(form)
        self._populate_lists()

        btn_row = QtWidgets.QHBoxLayout()
        self.status_lbl = QtWidgets.QLabel("")
        self.status_lbl.setObjectName("muted")
        btn_row.addWidget(self.status_lbl, 1)
        btn_cancel = QtWidgets.QPushButton("Άκυρο")
        btn_cancel.setObjectName("secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_ok = QtWidgets.QPushButton("Αποθήκευση")
        btn_ok.setObjectName("success")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _populate_lists(self):
        for c in self.db.list_categories():
            item = QtWidgets.QListWidgetItem(c["name"])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setData(QtCore.Qt.UserRole, c["id"])
            self.cat_list.addItem(item)
        libs = self.db.list_libraries()
        lib_id = libs[0]["id"] if libs else None
        for s in self.db.list_shelves(lib_id):
            item = QtWidgets.QListWidgetItem("  " * s["level"] + s["name"])
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setData(QtCore.Qt.UserRole, s["id"])
            self.shelf_list.addItem(item)

    def _add_new_cat(self):
        name = self.ed_new_cat.text().strip()
        if not name:
            return
        res = self.db.add_category(name)
        if res.get("ok"):
            item = QtWidgets.QListWidgetItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, res["id"])
            self.cat_list.addItem(item)
            self.ed_new_cat.clear()

    def _load_book(self, b):
        self.ed_number.setText(b.get("book_number", "") or "")
        self.ed_isbn.setText(b.get("isbn", "") or "")
        self.ed_title.setText(b.get("title", "") or "")
        self.ed_author.setText(b.get("author", "") or "")
        self.ed_publisher.setText(b.get("publisher", "") or "")
        self.ed_edition.setText(b.get("edition", "") or "")
        self.ed_year.setText(b.get("year", "") or "")
        self.sp_pages.setValue(b.get("pages") or 0)
        self.sp_copies.setValue(b.get("copies") or 1)
        self.ed_dewey.setText(b.get("dewey", "") or "")
        self.ed_tags.setText(", ".join(b.get("tags", [])))
        self.ed_notes.setPlainText(b.get("notes", "") or "")
        for i in range(self.cat_list.count()):
            item = self.cat_list.item(i)
            if item.text() in b.get("categories", []):
                item.setCheckState(QtCore.Qt.Checked)
        for i in range(self.shelf_list.count()):
            item = self.shelf_list.item(i)
            if item.text().strip() in b.get("shelves", []):
                item.setCheckState(QtCore.Qt.Checked)

    def _lookup_isbn(self):
        isbn = self.ed_isbn.text().strip()
        if not isbn:
            QtWidgets.QMessageBox.information(self, "ISBN", "Συμπληρώστε πρώτα ISBN.")
            return
        self.btn_isbn.setEnabled(False)
        self.btn_isbn.setText("Αναζήτηση...")
        self.status_lbl.setText("Γίνεται αναζήτηση στο διαδίκτυο...")
        self._worker = IsbnWorker()
        self._worker.finished.connect(self._apply_lookup)
        self._worker.failed.connect(self._lookup_failed)
        self._worker.start(isbn)

    def _apply_lookup(self, result):
        self._lookup_done()
        if result:
            if result.get("title"):
                self.ed_title.setText(result["title"])
            if result.get("author"):
                self.ed_author.setText(result["author"])
            if result.get("publisher"):
                self.ed_publisher.setText(result["publisher"])
            if result.get("year"):
                self.ed_year.setText(str(result["year"]))
            if result.get("pages"):
                self.sp_pages.setValue(int(result["pages"]))
            self.status_lbl.setText("Τα στοιχεία συμπληρώθηκαν από το διαδίκτυο.")
        else:
            self.status_lbl.setText("Δεν βρέθηκαν στοιχεία για αυτό το ISBN.")

    def _lookup_failed(self, msg):
        self._lookup_done()
        msg = (msg or "")
        if "429" in msg:
            self.status_lbl.setText(
                "Οι υπηρεσίες είναι προσωρινά απασχολημένες (429). Δοκιμάστε ξανά σε λίγο ή συμπληρώστε τα στοιχεία χειροκίνητα.")
        elif "timeout" in msg.lower() or "Χρονικό" in msg:
            self.status_lbl.setText("Η αναζήτηση άργησε να απαντήσει. Ελέγξτε το διαδίκτυο και δοκιμάστε ξανά.")
        elif "connection" in msg.lower() or "internet" in msg.lower():
            self.status_lbl.setText("Δεν υπάρχει σύνδεση στο διαδίκτυο. Συμπληρώστε τα στοιχεία χειροκίνητα.")
        else:
            self.status_lbl.setText("Αποτυχία αναζήτησης. Συμπληρώστε τα στοιχεία χειροκίνητα.")

    def _lookup_done(self):
        self.btn_isbn.setEnabled(True)
        self.btn_isbn.setText("Αυτόματη συμπλήρωση από ISBN")

    def result_data(self):
        cats = [item.data(QtCore.Qt.UserRole) for item in self.cat_list.findItems(
            "*", QtCore.Qt.MatchWildcard) if item.checkState() == QtCore.Qt.Checked]
        shelves = [item.data(QtCore.Qt.UserRole) for item in self.shelf_list.findItems(
            "*", QtCore.Qt.MatchWildcard) if item.checkState() == QtCore.Qt.Checked]
        tags = [t.strip() for t in self.ed_tags.text().split(",") if t.strip()]
        return {
            "book_number": self.ed_number.text().strip(),
            "isbn": self.ed_isbn.text().strip(),
            "title": self.ed_title.text().strip(),
            "author": self.ed_author.text().strip(),
            "publisher": self.ed_publisher.text().strip(),
            "edition": self.ed_edition.text().strip(),
            "year": self.ed_year.text().strip(),
            "pages": self.sp_pages.value(),
            "copies": self.sp_copies.value(),
            "dewey": self.ed_dewey.text().strip(),
            "categories": cats,
            "shelves": shelves,
            "tags": tags,
            "notes": self.ed_notes.toPlainText().strip(),
        }

    def _accept(self):
        data = self.result_data()
        if not data["title"]:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", "Ο τίτλος είναι υποχρεωτικός.")
            return
        self._data = data
        self.accept()