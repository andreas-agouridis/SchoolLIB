import os

from PySide6 import QtCore, QtWidgets

from services import importer, exporter
from ui.icons import make_icon
from ui.widgets.dropzone import DropZone


class ImportPage(QtWidgets.QWidget):
    FIELDS = {
        "books": importer.BOOK_FIELDS,
        "members": importer.MEMBER_FIELDS,
        "loans": importer.LOAN_FIELDS,
    }
    LABELS = {
        "books": {
            "title": "Τίτλος *", "author": "Συγγραφέας", "isbn": "ISBN",
            "book_number": "Αριθμός βιβλίου", "publisher": "Εκδότης",
            "edition": "Έκδοση", "year": "Έτος", "pages": "Σελίδες",
            "dewey": "Dewey", "copies": "Αντίτυπα", "notes": "Σημειώσεις",
            "categories": "Κατηγορίες", "tags": "Ετικέτες", "shelves": "Ράφι/Τοποθεσία"},
        "members": {
            "name": "Όνομα *", "member_number": "Αριθμός μέλους", "class": "Τάξη",
            "email": "Email", "phone": "Τηλέφωνο", "notes": "Σημειώσεις"},
        "loans": {
            "member_number": "Κωδικός μέλους *", "book_number": "Κωδικός βιβλίου *",
            "loan_date": "Ημερομηνία δανεισμού", "due_date": "Προθεσμία",
            "return_date": "Επιστροφή", "renewals": "Ανανεώσεις"},
    }

    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.setObjectName("page")
        self.kind = "books"
        self.data = None
        self.headers = []
        self.mapping = {}
        self._map_combos = {}
        self.file_path = None
        self._build()

    def _build(self):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        hdr = QtWidgets.QLabel("Εισαγωγή από αρχείο")
        hdr.setObjectName("header")
        outer.addWidget(hdr)
        hint = QtWidgets.QLabel(
            "Σύρετε εύκολα βιβλία, μέλη και δάνεια από Excel, CSV ή από άλλα προγράμματα. "
            "Ο οδηγός αναγνωρίζει μόνος του τις στήλες και σας ζητάει να επιβεβαιώσετε.",
            objectName="muted")
        hint.setWordWrap(True)
        outer.addWidget(hint)

        self.btn_books = QtWidgets.QPushButton("Βιβλία")
        self.btn_members = QtWidgets.QPushButton("Μέλη")
        self.btn_loans = QtWidgets.QPushButton("Δάνεια")
        self.btn_group = QtWidgets.QButtonGroup(self)
        self.btn_group.setExclusive(True)
        for i, (b, kind) in enumerate([
            (self.btn_books, "books"),
            (self.btn_members, "members"),
            (self.btn_loans, "loans"),
        ]):
            b.setObjectName("ghost")
            b.setCheckable(True)
            self.btn_group.addButton(b, i)
        self.btn_books.setChecked(True)
        self.btn_group.idClicked.connect(self._kind_changed_id)
        kind_row = QtWidgets.QHBoxLayout()
        kind_row.setSpacing(8)
        kind_row.addWidget(self.btn_books)
        kind_row.addWidget(self.btn_members)
        kind_row.addWidget(self.btn_loans)
        kind_row.addStretch()
        outer.addLayout(kind_row)

        self.zone = DropZone()
        self.zone.file_selected.connect(self._load_file)
        outer.addWidget(self.zone)

        self.file_card = QtWidgets.QFrame()
        self.file_card.setObjectName("card")
        fc = QtWidgets.QHBoxLayout(self.file_card)
        fc.setContentsMargins(12, 10, 12, 10)
        self.lbl_file = QtWidgets.QLabel("")
        self.lbl_file.setObjectName("muted")
        self.lbl_file.setWordWrap(True)
        fc.addWidget(self.lbl_file, 1)
        self.btn_template = QtWidgets.QPushButton(" Λήψη προτύπου")
        self.btn_template.setIcon(make_icon("template", "#333333", 18))
        self.btn_template.setObjectName("secondary")
        self.btn_template.clicked.connect(self._download_template)
        fc.addWidget(self.btn_template)
        self.btn_clear = QtWidgets.QPushButton(" Καθαρό")
        self.btn_clear.setIcon(make_icon("delete", "#333333", 18))
        self.btn_clear.setObjectName("secondary")
        self.btn_clear.clicked.connect(self._reset)
        fc.addWidget(self.btn_clear)
        self.file_card.hide()
        outer.addWidget(self.file_card)

        self.preview = QtWidgets.QTableWidget()
        self.preview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preview.setMaximumHeight(180)
        outer.addWidget(self.preview)

        self.map_card = QtWidgets.QFrame()
        self.map_card.setObjectName("card")
        mo = QtWidgets.QVBoxLayout(self.map_card)
        mo.setContentsMargins(12, 10, 12, 10)
        mo.setSpacing(6)
        mo.addWidget(QtWidgets.QLabel("Αντιστοίχιση στηλών"))
        mo.addWidget(QtWidgets.QLabel(
            "Αλλάξτε εάν χρειαστεί. Τα πεδία με * είναι υποχρεωτικά.", objectName="muted"))
        self.map_form = QtWidgets.QFormLayout()
        self.map_form.setSpacing(6)
        self.map_container = QtWidgets.QWidget()
        self.map_container.setLayout(self.map_form)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.map_container)
        scroll.setMaximumHeight(250)
        mo.addWidget(scroll)
        self.map_card.hide()
        outer.addWidget(self.map_card)

        self.opts_card = QtWidgets.QFrame()
        self.opts_card.setObjectName("card")
        ol = QtWidgets.QHBoxLayout(self.opts_card)
        ol.setContentsMargins(12, 10, 12, 10)
        self.chk_skip = QtWidgets.QCheckBox("Παράλειψη διπλοτύπων")
        self.chk_skip.setChecked(True)
        self.chk_update = QtWidgets.QCheckBox("Ενημέρωση υπαρχόντων")
        ol.addWidget(self.chk_skip)
        ol.addWidget(self.chk_update)
        ol.addStretch()
        self.opts_card.hide()
        outer.addWidget(self.opts_card)

        self.btn_run = QtWidgets.QPushButton(" Καταχώρηση δεδομένων")
        self.btn_run.setIcon(make_icon("check", "#ffffff", 18))
        self.btn_run.setObjectName("success big")
        self.btn_run.clicked.connect(self._run_import)
        self.btn_run.hide()
        outer.addWidget(self.btn_run)

        self.report_card = QtWidgets.QFrame()
        self.report_card.setObjectName("card")
        rl = QtWidgets.QVBoxLayout(self.report_card)
        rl.setContentsMargins(12, 10, 12, 10)
        rl.setSpacing(6)
        self.lbl_report = QtWidgets.QLabel("")
        self.lbl_report.setObjectName("muted")
        self.lbl_report.setWordWrap(True)
        rl.addWidget(self.lbl_report)
        self.report_list = QtWidgets.QListWidget()
        self.report_list.setMaximumHeight(180)
        rl.addWidget(self.report_list)
        self.btn_again = QtWidgets.QPushButton(" Νέα εισαγωγή")
        self.btn_again.setIcon(make_icon("refresh", "#333333", 18))
        self.btn_again.setObjectName("secondary")
        self.btn_again.clicked.connect(self._reset)
        rl.addWidget(self.btn_again)
        self.report_card.hide()
        outer.addWidget(self.report_card)
        outer.addStretch()

    def _kind_changed_id(self, idx):
        mapping = {0: "books", 1: "members", 2: "loans"}
        self.kind = mapping.get(idx, "books")
        if self.data:
            self._build_mapping()

    def _download_template(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Πρότυπο", f"ypodeigma_{self.kind}.xlsx", "Excel (*.xlsx)")
        if not path:
            return
        importer.export_template(path, kind=self.kind)
        self.main.status_message("Το πρότυπο αποθηκεύτηκε.")

    def _load_file(self, path):
        try:
            data = importer.read_rows_file(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Σφάλμα", f"Δεν ήταν δυνατό να ανοιχτεί:\n{e}")
            return
        self.file_path = path
        self.data = data
        self.headers = data["headers"] or []
        self.preview.setColumnCount(max(1, len(self.headers)))
        self.preview.setHorizontalHeaderLabels(self.headers or ["(χωρίς επικεφαλίδες)"])
        shown = (data["rows"] or [])[:10]
        self.preview.setRowCount(len(shown))
        for r, row in enumerate(shown):
            for c, h in enumerate(self.headers or []):
                self.preview.setItem(r, c, QtWidgets.QTableWidgetItem(str(row.get(h, ""))))
        fname = os.path.basename(path)
        n = len(data["rows"])
        self.lbl_file.setText(f"{fname} — {n} γραμμές.")
        self.file_card.show()
        self.zone.hide()
        self._build_mapping()
        self.map_card.show()
        self.opts_card.show()
        self.btn_run.show()
        self.report_card.hide()

    def _build_mapping(self):
        while self.map_form.count():
            item = self.map_form.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._map_combos = {}
        fields = self.FIELDS[self.kind]
        self.mapping, _ = importer.guess_mapping(self.headers, fields)
        for f in fields:
            lbl = QtWidgets.QLabel(self.LABELS[self.kind].get(f, f))
            cmb = QtWidgets.QComboBox()
            cmb.setObjectName("secondary")
            cmb.addItem("(να αγνοηθεί)", None)
            for h in self.headers:
                cmb.addItem(h, h)
            guessed = self.mapping.get(f)
            idx = cmb.findData(guessed)
            if idx >= 0:
                cmb.setCurrentIndex(idx)
            self.map_form.addRow(lbl, cmb)
            self._map_combos[f] = cmb

    def _current_mapping(self):
        mapping = {}
        for f, cmb in self._map_combos.items():
            val = cmb.currentData()
            if val is not None:
                mapping[f] = val
        return mapping

    def _run_import(self):
        mapping = self._current_mapping()
        required = {"books": ["title"], "members": ["name"],
                     "loans": ["member_number", "book_number"]}[self.kind]
        missing = [f for f in required if not mapping.get(f)]
        if missing:
            QtWidgets.QMessageBox.warning(
                self, "Αντιστοίχιση",
                "Ορίστε τις υποχρεωτικές στήλες: " + ", ".join(
                    self.LABELS[self.kind].get(f, f) for f in missing))
            return
        rows = (self.data or {}).get("rows", [])
        skip = self.chk_skip.isChecked()
        update = self.chk_update.isChecked()
        try:
            if self.kind == "books":
                report = importer.import_books(self.db, rows, mapping,
                                               skip_duplicates=skip, update_existing=update)
                kind_name = "Βιβλία"
            elif self.kind == "members":
                report = importer.import_members(self.db, rows, mapping,
                                                 skip_duplicates=skip)
                kind_name = "Μέλη"
            else:
                report = importer.import_loans(self.db, rows, mapping,
                                               due_days=self.main.settings.due_days)
                kind_name = "Δάνεια"
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Σφάλμα εισαγωγής", str(e))
            return
        self.lbl_report.setText(
            f"{kind_name}: {report['imported']} εισήχθηκαν, {report.get('updated', 0)} ενημερώθηκαν, "
            f"{report['skipped']} παραλείφθηκαν.")
        self.report_list.clear()
        errors = report.get("errors", [])[:300]
        for e in errors:
            self.report_list.addItem(e)
        if not errors:
            self.report_list.addItem("Χωρίς σφάλματα — όλα καταχωρήθηκαν.")
        self.map_card.hide()
        self.opts_card.hide()
        self.btn_run.hide()
        self.report_card.show()
        self.main.refresh_pages()

    def _reset(self):
        self.data = None
        self.headers = []
        self.mapping = {}
        self._map_combos = {}
        self.file_path = None
        self.zone.show()
        self.file_card.hide()
        self.preview.clearContents()
        self.preview.setRowCount(0)
        self.preview.setColumnCount(0)
        self.map_card.hide()
        self.opts_card.hide()
        self.btn_run.hide()
        self.report_card.hide()

    def refresh(self):
        pass