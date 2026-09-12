import datetime

from PySide6 import QtCore, QtGui, QtWidgets

from services import exporter
from services.printing import reminders_pdf
from ui.icons import make_icon
from ui.widgets.table_helpers import make_table, fill_table, selected_data, SearchBar
from ui.widgets.loan_dialog import LoanDialog, pick_active_loan
from ui import theme


class LoansPage(QtWidgets.QWidget):
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
        header = QtWidgets.QLabel("Δάνεια")
        header.setObjectName("header")
        layout.addWidget(header)

        self.tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.tabs, 1)
        self._build_active_tab()
        self._build_history_tab()

    def _build_active_tab(self):
        tab = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(tab)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(10)
        self.active_search = SearchBar("Αναζήτηση σε βιβλία ή μέλη")
        self.active_search.search_requested.connect(self.refresh)
        v.addWidget(self.active_search)

        self.active_table = make_table(["Βιβλίο", "Μέλος", "Δανείστηκε", "Προθεσμία", "Υπόλοιπο", "Ανανεώσεις"])
        self.active_table.horizontalHeader().setStretchLastSection(True)
        v.addWidget(self.active_table, 1)

        btns = QtWidgets.QHBoxLayout()
        btn_loan = QtWidgets.QPushButton(" Νέος δανεισμός")
        btn_loan.setIcon(make_icon("add", "#ffffff", 18))
        btn_loan.setObjectName("success")
        btn_loan.clicked.connect(self._new_loan)
        btns.addWidget(btn_loan)
        btn_return = QtWidgets.QPushButton(" Επιστροφή")
        btn_return.setIcon(make_icon("return", "#ffffff", 18))
        btn_return.clicked.connect(self._return)
        btns.addWidget(btn_return)
        btn_renew = QtWidgets.QPushButton(" Παράταση")
        btn_renew.setIcon(make_icon("extend", "#ffffff", 18))
        btn_renew.clicked.connect(self._renew)
        btns.addWidget(btn_renew)
        btn_remind = QtWidgets.QPushButton(" Εκτύπωση υπενθυμίσεων")
        btn_remind.setIcon(make_icon("print", "#ffffff", 18))
        btn_remind.clicked.connect(self._print_reminders)
        btns.addWidget(btn_remind)
        btn_export = QtWidgets.QPushButton(" Εξαγωγή")
        btn_export.setIcon(make_icon("export", "#ffffff", 18))
        btn_export.clicked.connect(self._export_active)
        btns.addWidget(btn_export)
        btns.addStretch()
        v.addLayout(btns)
        self.tabs.addTab(tab, "Ενεργά Δάνεια")

    def _build_history_tab(self):
        tab = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(tab)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(10)
        self.history_search = SearchBar("Αναζήτηση σε βιβλία ή μέλη")
        self.history_search.search_requested.connect(self.refresh)
        v.addWidget(self.history_search)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Τύπος:"))
        self.cmb_status = QtWidgets.QComboBox()
        self.cmb_status.addItem("Όλα", None)
        self.cmb_status.addItem("Μόνο ενεργά", False)
        self.cmb_status.addItem("Μόνο επιστραφέντα", True)
        self.cmb_status.currentIndexChanged.connect(self.refresh)
        row.addWidget(self.cmb_status)
        row.addWidget(QtWidgets.QLabel("Από:"))
        self.de_from = QtWidgets.QDateEdit()
        self.de_from.setCalendarPopup(True)
        self.de_from.setDate(self.de_from.minimumDate())
        self.de_from.setDisplayFormat("dd/MM/yyyy")
        self.de_from.dateChanged.connect(self.refresh)
        row.addWidget(self.de_from)
        row.addWidget(QtWidgets.QLabel("Έως:"))
        self.de_to = QtWidgets.QDateEdit()
        self.de_to.setCalendarPopup(True)
        self.de_to.setDate(datetime.date.today())
        self.de_to.setDisplayFormat("dd/MM/yyyy")
        self.de_to.dateChanged.connect(self.refresh)
        row.addWidget(self.de_to)
        row.addStretch()
        v.addLayout(row)

        self.history_table = make_table(["Ημερομηνία", "Βιβλίο", "Μέλος", "Δανείστηκε",
                                         "Προθεσμία", "Επιστροφή", "Ανανεώσεις"])
        v.addWidget(self.history_table, 1)

        btns = QtWidgets.QHBoxLayout()
        btn_export = QtWidgets.QPushButton(" Εξαγωγή")
        btn_export.setIcon(make_icon("export", "#ffffff", 18))
        btn_export.clicked.connect(self._export_history)
        btns.addWidget(btn_export)
        btn_delete = QtWidgets.QPushButton(" Διαγραφή επιλεγμένου")
        btn_delete.setIcon(make_icon("delete", "#ffffff", 18))
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self._delete_history)
        btns.addWidget(btn_delete)
        btns.addStretch()
        v.addLayout(btns)
        self.tabs.addTab(tab, "Ιστορικό Δανείων")

    def refresh(self):
        if self.tabs.currentIndex() == 0:
            self._refresh_active()
        else:
            self._refresh_history()

    def _refresh_active(self):
        loans = self.db.active_loans(q=self.active_search.text())
        fill_table(self.active_table, loans,
                   ["book_title", "member_name", "loan_date", "due_date", "days_left", "renewals"])
        for r in range(self.active_table.rowCount()):
            item = self.active_table.item(r, 0)
            data = item.data(QtCore.Qt.UserRole)
            if not data:
                continue
            days = data.get("days_left", 0)
            bg = None
            if days < 0:
                bg = QtGui.QColor("#fdecea")
            elif days <= int(self.main.settings.remind_days):
                bg = QtGui.QColor("#fdf3d7")
            if bg:
                for c in range(self.active_table.columnCount()):
                    self.active_table.item(r, c).setBackground(QtGui.QBrush(bg))
            label = "Ληξιπρόθεσμο" if days < 0 else (f"Υπολείπονται {days} ημέρες" if days > 0 else "Λήγει σήμερα")
            self.active_table.item(r, 4).setToolTip(label)

    def _refresh_history(self):
        d_from = self.de_from.date().toPython()
        d_to = self.de_to.date().toPython()
        returned = self.cmb_status.currentData()
        rows = self.db.loan_history(q=self.history_search.text(),
                                    date_from=d_from.isoformat(),
                                    date_to=d_to.isoformat(),
                                    returned=returned)
        fill_table(self.history_table, rows,
                   ["loan_date", "book_title", "member_name", "loan_date", "due_date",
                    "return_date", "renewals"])
        for r in range(self.history_table.rowCount()):
            item = self.history_table.item(r, 4)
            if item and item.text():
                data = item.data(QtCore.Qt.UserRole)
                if data and data.get("return_date"):
                    item = self.history_table.item(r, 0)
                    item.setForeground(QtGui.QBrush(QtGui.QColor(theme.TEXT_MUTED)))

    def _new_loan(self):
        dlg = LoanDialog(self.db, self, due_days=self.main.settings.due_days)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            member = getattr(dlg, "_member")
            b = getattr(dlg, "_book")
            if len(self.db.member_active_loans(member["id"])) >= self.main.settings.max_loans:
                QtWidgets.QMessageBox.warning(self, "Όριο δανεισμού",
                                              f"Το μέλος έχει φτάσει το όριο ({self.main.settings.max_loans}).")
                return
            res = self.db.loan_book(b["id"], member["id"], due_days=getattr(dlg, "_days"))
            if res.get("ok"):
                self.main.status_message(f"Δανεισμός ολοκληρώθηκε, προθεσμία {res['due_date']}.")
            else:
                QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
            self.refresh()
            self.main.refresh_pages()

    def _return(self):
        loan = pick_active_loan(self.db, self, "Επιστροφή Βιβλίου")
        if not loan:
            return
        res = self.db.return_book(loan["id"])
        if res.get("ok"):
            self.main.status_message("Το βιβλίο επιστράφηκε.")
        else:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
        self.refresh()
        self.main.refresh_pages()

    def _renew(self):
        loan = pick_active_loan(self.db, self, "Παράταση Δανείου")
        if not loan:
            return
        days, ok = QtWidgets.QInputDialog.getInt(self, "Παράταση",
                                                 "Ημέρες παράτασης:", 7, 1, 365)
        if not ok:
            return
        res = self.db.renew_loan(loan["id"], days)
        if res.get("ok"):
            self.main.status_message(f"Παράταση έως {res['due_date']}.")
        else:
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
        self.refresh()

    def _print_reminders(self):
        remind = int(self.main.settings.remind_days)
        loans = self.db.overdue_loans() + self.db.upcoming_loans(remind)
        if not loans:
            QtWidgets.QMessageBox.information(self, "Υπενθυμίσεις",
                                              "Δεν υπάρχουν ληξιπρόθεσμα ή επικείμενα δάνεια.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Αποθήκευση υπενθυμίσεων",
                                                        "upenthimiseis.pdf", "PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        seen = set()
        uniq = []
        for l in loans:
            if l["id"] in seen:
                continue
            seen.add(l["id"])
            uniq.append(l)
        reminders_pdf(uniq, path, school_name=self.main.settings.school_name)
        self.main.status_message(f"Δημιουργήθηκαν υπενθυμίσεις για {len(uniq)} δάνεια.")

    def _export_active(self):
        rows = self.db.active_loans(q=self.active_search.text())
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν δάνεια.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Εξαγωγή δανείων", "energa_daneia.xlsx",
                                                        "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        data = []
        for l in rows:
            d = dict(l)
            d["member"] = d.pop("member_name", "")
            d["book"] = d.pop("book_title", "")
            d["status"] = ("Υπερημερία" if l["days_left"] < 0
                           else ("Λήγει σύντομα" if l["days_left"] <= int(self.main.settings.remind_days) else "Κανονικό"))
            data.append(d)
        exporter.export_rows(data, ["book", "member", "loan_date", "due_date", "status", "renewals"],
                             path, fmt=fmt, title="Ενεργά Δάνεια", school_name=self.main.settings.school_name)
        self.main.status_message(f"Εξήχθησαν {len(data)} δάνεια.")

    def _export_history(self):
        rows = self.db.loan_history(q=self.history_search.text(),
                                    date_from=self.de_from.date().toPython().isoformat(),
                                    date_to=self.de_to.date().toPython().isoformat(),
                                    returned=self.cmb_status.currentData())
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν εγγραφές.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Εξαγωγή ιστορικού", "istoriko_daneiwn.xlsx",
                                                        "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        data = [dict(r) for r in rows]
        exporter.export_rows(data, ["loan_date", "book_title", "book_number", "member_name",
                                    "member_number", "due_date", "return_date", "renewals"],
                             path, fmt=fmt, title="Ιστορικό Δανείων", school_name=self.main.settings.school_name)
        self.main.status_message(f"Εξήχθησαν {len(data)} εγγραφές.")

    def _delete_history(self):
        rows = selected_data(self.history_table)
        if not rows:
            QtWidgets.QMessageBox.information(self, "Ιστορικό", "Επιλέξτε εγγραφές.")
            return
        ret = QtWidgets.QMessageBox.question(self, "Διαγραφή",
                                             f"Διαγραφή {len(rows)} εγγραφών ιστορικού;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        for r in rows:
            self.db.delete_loan(r["id"])
        self.main.status_message(f"Διαγράφηκαν {len(rows)} εγγραφές.")
        self.refresh()