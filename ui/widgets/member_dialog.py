from PySide6 import QtCore, QtWidgets


class MemberDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None, member=None):
        super().__init__(parent)
        self.db = db
        self.member = member
        self.setWindowTitle("Επεξεργασία Μέλους" if member else "Προσθήκη Μέλους")
        self.resize(440, 400)
        self._build()
        if member:
            self._load(member)

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        form.setSpacing(10)
        self.ed_number = QtWidgets.QLineEdit()
        form.addRow("Αριθμός μέλους:", self.ed_number)
        self.ed_name = QtWidgets.QLineEdit()
        form.addRow("Ονοματεπώνυμο *:", self.ed_name)
        self.ed_class = QtWidgets.QLineEdit()
        form.addRow("Τάξη / Τμήμα:", self.ed_class)
        self.ed_email = QtWidgets.QLineEdit()
        form.addRow("Email:", self.ed_email)
        self.ed_phone = QtWidgets.QLineEdit()
        form.addRow("Τηλέφωνο:", self.ed_phone)
        self.ed_notes = QtWidgets.QTextEdit()
        self.ed_notes.setMaximumHeight(90)
        form.addRow("Σημειώσεις:", self.ed_notes)
        layout.addLayout(form)
        layout.addStretch()

        btn_row = QtWidgets.QHBoxLayout()
        btn_cancel = QtWidgets.QPushButton("Άκυρο")
        btn_cancel.setObjectName("secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)
        btn_row.addStretch()
        btn_ok = QtWidgets.QPushButton("Αποθήκευση")
        btn_ok.setObjectName("success")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._accept)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _load(self, m):
        self.ed_number.setText(m.get("member_number", "") or "")
        self.ed_name.setText(m.get("name", "") or "")
        self.ed_class.setText(m.get("class", "") or "")
        self.ed_email.setText(m.get("email", "") or "")
        self.ed_phone.setText(m.get("phone", "") or "")
        self.ed_notes.setPlainText(m.get("notes", "") or "")

    def result_data(self):
        return {
            "member_number": self.ed_number.text().strip(),
            "name": self.ed_name.text().strip(),
            "class": self.ed_class.text().strip(),
            "email": self.ed_email.text().strip(),
            "phone": self.ed_phone.text().strip(),
            "notes": self.ed_notes.toPlainText().strip(),
        }

    def _accept(self):
        data = self.result_data()
        if not data["name"]:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", "Το όνομα είναι υποχρεωτικό.")
            return
        self._data = data
        self.accept()