import datetime

from PySide6 import QtCore, QtWidgets

from ui.widgets.autocomplete import FilterComboBox


class LoanDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None, book=None, member=None, due_days=14):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Δανεισμός Βιβλίου")
        self.resize(520, 320)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Επιλέξτε μέλος και βιβλίο για να ολοκληρωθεί ο δανεισμός:"))

        f = QtWidgets.QFormLayout()
        f.setSpacing(8)
        self.cmb_member = FilterComboBox()
        members = self.db.list_members()
        self.cmb_member.set_items(members, display_key="name", search_keys=["name", "member_number", "class"])
        f.addRow("Μέλος:", self.cmb_member)
        self.cmb_book = FilterComboBox()
        books = self.db.search_books("", limit=800)
        self.cmb_book.set_items(books, display_key="title", search_keys=["title", "author", "isbn", "book_number"])
        f.addRow("Βιβλίο:", self.cmb_book)
        self.sp_days = QtWidgets.QSpinBox()
        self.sp_days.setRange(1, 366)
        self.sp_days.setValue(int(due_days or 14))
        f.addRow("Ημέρες δανεισμού:", self.sp_days)
        layout.addLayout(f)
        layout.addStretch()

        self.info_lbl = QtWidgets.QLabel("")
        self.info_lbl.setObjectName("muted")
        layout.addWidget(self.info_lbl)

        btn_row = QtWidgets.QHBoxLayout()
        btn_cancel = QtWidgets.QPushButton("Άκυρο")
        btn_cancel.setObjectName("secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_ok = QtWidgets.QPushButton("Δανεισμός")
        btn_ok.setObjectName("success")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

        if book:
            idx = self.cmb_book.findText(book.get("title", ""))
            if idx >= 0:
                self.cmb_book.setCurrentIndex(idx)
        if member:
            idx = self.cmb_member.findText(member.get("name", ""))
            if idx >= 0:
                self.cmb_member.setCurrentIndex(idx)

        self.cmb_book.currentIndexChanged.connect(self._update_info)
        self.cmb_member.currentIndexChanged.connect(self._update_info)
        self._update_info()

    def _update_info(self):
        book = self.cmb_book.current_item()
        member = self.cmb_member.current_item()
        parts = []
        if member:
            act = self.db.member_active_loans(member.get("id"))
            parts.append(f"Μέλος: {len(act)} ενεργά δάνεια")
        if book:
            parts.append(f"Βιβλίο: {book.get('available', 0)} διαθέσιμα αντίτυπα")
        self.info_lbl.setText("  •  ".join(parts))

    def _accept(self):
        member = self.cmb_member.current_item()
        book = self.cmb_book.current_item()
        if not member:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", "Επιλέξτε μέλος.")
            return
        if not book:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", "Επιλέξτε βιβλίο.")
            return
        self._member = member
        self._book = book
        self._days = self.sp_days.value()
        self.accept()


def pick_active_loan(db, parent, title="Επιλέξτε δάνειο"):
    loans = db.active_loans()
    if not loans:
        QtWidgets.QMessageBox.information(parent, "Δάνεια", "Δεν υπάρχουν ενεργά δάνεια.")
        return None
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.resize(640, 420)
    layout = QtWidgets.QVBoxLayout(dlg)
    layout.addWidget(QtWidgets.QLabel("Επιλέξτε δάνειο από τη λίστα:"))
    lw = QtWidgets.QListWidget()
    for l in loans:
        overdue = l["days_left"] < 0
        label = (f"{l['book_title']}  [{l['book_number']}] -> {l['member_name']}  "
                 f"(προθεσμία {l['due_date']}, υπόλοιπο {l['days_left']} ημέρες)")
        item = QtWidgets.QListWidgetItem(label)
        if overdue:
            item.setForeground(QtWidgets.qApp.palette().color(QtWidgets.QPalette.Highlight))
        item.setData(QtCore.Qt.UserRole, l)
        lw.addItem(item)
    layout.addWidget(lw, 1)
    btn_row = QtWidgets.QHBoxLayout()
    btn_ok = QtWidgets.QPushButton("ΟΚ")
    btn_ok.setObjectName("success")
    btn_ok.clicked.connect(dlg.accept)
    btn_cancel = QtWidgets.QPushButton("Άκυρο")
    btn_cancel.setObjectName("secondary")
    btn_cancel.clicked.connect(dlg.reject)
    btn_row.addWidget(btn_cancel)
    btn_row.addStretch()
    btn_row.addWidget(btn_ok)
    layout.addLayout(btn_row)
    if dlg.exec_() != QtWidgets.QDialog.Accepted:
        return None
    item = lw.currentItem()
    if not item:
        return None
    return item.data(QtCore.Qt.UserRole)