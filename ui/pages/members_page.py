from PySide6 import QtCore, QtWidgets

from services import exporter
from services.printing import member_cards_pdf
from ui.icons import make_icon
from ui.widgets.table_helpers import make_table, fill_table, selected_data, SearchBar
from ui.widgets.member_dialog import MemberDialog
from ui.widgets.loan_dialog import LoanDialog


class MembersPage(QtWidgets.QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.setObjectName("page")
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        header = QtWidgets.QLabel("Μέλη")
        header.setObjectName("header")
        layout.addWidget(header)

        top = QtWidgets.QHBoxLayout()
        self.search = SearchBar("Αναζήτηση ονοματεπωνύμου ή αριθμού μέλους")
        self.search.search_requested.connect(self.refresh)
        top.addWidget(self.search, 1)
        top.addWidget(QtWidgets.QLabel("Τάξη:"))
        self.cmb_class = QtWidgets.QComboBox()
        self.cmb_class.addItem("Όλες οι τάξεις", None)
        self.cmb_class.currentIndexChanged.connect(self.refresh)
        top.addWidget(self.cmb_class)
        layout.addLayout(top)

        self.table = make_table(["Ονοματεπώνυμο", "Αριθμός", "Τάξη", "Email", "Τηλέφωνο", "Ενεργά Δάνεια"])
        self.table.hideColumn(1)
        self.table.doubleClicked.connect(self._edit)
        layout.addWidget(self.table, 1)

        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(8)
        btn_add = QtWidgets.QPushButton(" Προσθήκη μέλους")
        btn_add.setIcon(make_icon("add", "#ffffff", 18))
        btn_add.setObjectName("success")
        btn_add.clicked.connect(self._add)
        buttons.addWidget(btn_add)
        btn_edit = QtWidgets.QPushButton(" Επεξεργασία")
        btn_edit.setIcon(make_icon("edit", "#ffffff", 18))
        btn_edit.clicked.connect(self._edit)
        buttons.addWidget(btn_edit)
        btn_delete = QtWidgets.QPushButton(" Διαγραφή")
        btn_delete.setIcon(make_icon("delete", "#ffffff", 18))
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self._delete)
        buttons.addWidget(btn_delete)
        btn_cards = QtWidgets.QPushButton(" Εκτύπωση καρτελών")
        btn_cards.setIcon(make_icon("print", "#ffffff", 18))
        btn_cards.clicked.connect(self._print_cards)
        buttons.addWidget(btn_cards)
        btn_loans = QtWidgets.QPushButton(" Δανεισμός")
        btn_loans.setIcon(make_icon("loan", "#ffffff", 18))
        btn_loans.clicked.connect(self._loan)
        buttons.addWidget(btn_loans)
        btn_export = QtWidgets.QPushButton(" Εξαγωγή")
        btn_export.setIcon(make_icon("export", "#ffffff", 18))
        btn_export.clicked.connect(self._export)
        buttons.addWidget(btn_export)
        btn_import = QtWidgets.QPushButton(" Εισαγωγή")
        btn_import.setIcon(make_icon("import", "#ffffff", 18))
        btn_import.clicked.connect(self.main.goto_import)
        buttons.addWidget(btn_import)
        buttons.addStretch()
        layout.addLayout(buttons)

    def _reload_classes(self):
        classes = self.db.member_classes()
        current = self.cmb_class.currentData()
        self.cmb_class.blockSignals(True)
        self.cmb_class.clear()
        self.cmb_class.addItem("Όλες οι τάξεις", None)
        for c in classes:
            self.cmb_class.addItem(c, c)
        idx = self.cmb_class.findData(current)
        if idx >= 0:
            self.cmb_class.setCurrentIndex(idx)
        self.cmb_class.blockSignals(False)

    def refresh(self):
        self._reload_classes()
        rows = self.db.list_members(q=self.search.text(), class_name=self.cmb_class.currentData())
        fill_table(self.table, rows, ["name", "member_number", "class", "email", "phone", "active_loans"])
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 5)
            if item and item.text() != "0":
                item.setForeground(QtCore.Qt.GlobalColor.darkRed)

    def _do_loan(self, npage=None):
        pass

    def _add(self):
        dlg = MemberDialog(self.db, self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.db.add_member(getattr(dlg, "_data"))
            self.main.status_message("Το μέλος προστέθηκε.")
            self.refresh()

    def _edit(self):
        rows = selected_data(self.table)
        if not rows:
            QtWidgets.QMessageBox.information(self, "Μέλη", "Επιλέξτε πρώτα ένα μέλος.")
            return
        m = rows[0]
        dlg = MemberDialog(self.db, self, member=m)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.db.update_member(m["id"], getattr(dlg, "_data"))
            self.main.status_message("Οι αλλαγές αποθηκεύτηκαν.")
            self.refresh()

    def _delete(self):
        rows = selected_data(self.table)
        if not rows:
            QtWidgets.QMessageBox.information(self, "Μέλη", "Επιλέξτε πρώτα μέλη.")
            return
        ret = QtWidgets.QMessageBox.question(self, "Διαγραφή",
                                             f"Διαγραφή {len(rows)} μέλους/ων;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        for m in rows:
            if m["active_loans"] > 0:
                QtWidgets.QMessageBox.warning(self, "Δεν γίνεται",
                                              f"Το μέλος {m['name']} έχει ενεργά δάνεια.")
                continue
            self.db.delete_member(m["id"])
        self.main.status_message("Τα μέλη διαγράφηκαν.")
        self.refresh()

    def _print_cards(self):
        rows = selected_data(self.table)
        if not rows:
            rows = self.db.list_members(q=self.search.text(), class_name=self.cmb_class.currentData())
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εκτύπωση", "Δεν υπάρχουν μέλη.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Αποθήκευση καρτελών", "kartele_elon.pdf",
                                                        "PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        member_cards_pdf(rows, path, school_name=self.main.settings.school_name)
        self.main.status_message(f"Δημιουργήθηκαν {len(rows)} καρτέλες: {path}")

    def _loan(self):
        rows = selected_data(self.table)
        member = rows[0] if rows else None
        dlg = LoanDialog(self.db, self, member=member, due_days=self.main.settings.due_days)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            mem = getattr(dlg, "_member")
            b = getattr(dlg, "_book")
            active = self.db.member_active_loans(mem["id"])
            if len(active) >= self.main.settings.max_loans:
                QtWidgets.QMessageBox.warning(self, "Όριο δανεισμού",
                                              f"Το μέλος έχει φτάσει το όριο ({self.main.settings.max_loans}).")
                return
            res = self.db.loan_book(b["id"], mem["id"], due_days=getattr(dlg, "_days"))
            if res.get("ok"):
                self.main.status_message(f"Δανεισμός ολοκληρώθηκε, προθεσμία {res['due_date']}.")
            else:
                QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
            self.refresh()
            self.main.refresh_pages()

    def _export(self):
        rows = self.db.list_members(q=self.search.text(), class_name=self.cmb_class.currentData())
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν μέλη.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Εξαγωγή μελών", "meli.xlsx",
                                                        "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        exporter.export_rows(rows, ["member_number", "name", "class", "email", "phone", "notes"],
                             path, fmt=fmt, title="Μέλη", school_name=self.main.settings.school_name)
        self.main.status_message(f"Εξήχθησαν {len(rows)} μέλη.")