from PySide6 import QtCore, QtGui, QtWidgets

from services import exporter
from ui import theme
from ui.icons import make_icon
from ui.widgets.table_helpers import make_table, fill_table, row_data, selected_data, SearchBar
from ui.widgets.book_dialog import BookDialog
from ui.widgets.loan_dialog import LoanDialog
from services.printing import book_labels_pdf


class BooksPage(QtWidgets.QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.setObjectName("page")
        self._filters = {}
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        layout.addWidget(QtWidgets.QLabel("Βιβλία"))
        header = layout.itemAt(layout.count() - 1).widget()
        header.setObjectName("header")

        self.search = SearchBar("Αναζήτηση τίτλου, συγγραφέα, ISBN ή αριθμού βιβλίου")
        self.search.search_requested.connect(self.refresh)
        layout.addWidget(self.search)

        filters_row = QtWidgets.QHBoxLayout()
        filters_row.setSpacing(8)
        self.cmb_library = QtWidgets.QComboBox()
        filters_row.addWidget(QtWidgets.QLabel("Βιβλιοθήκη:"))
        filters_row.addWidget(self.cmb_library)
        self.cmb_category = QtWidgets.QComboBox()
        filters_row.addWidget(QtWidgets.QLabel("Κατηγορία:"))
        filters_row.addWidget(self.cmb_category)
        self.cmb_shelf = QtWidgets.QComboBox()
        filters_row.addWidget(QtWidgets.QLabel("Ράφι:"))
        filters_row.addWidget(self.cmb_shelf)
        self.cmb_tag = QtWidgets.QComboBox()
        filters_row.addWidget(QtWidgets.QLabel("Ετικέτα:"))
        filters_row.addWidget(self.cmb_tag)
        filters_row.addStretch()
        self.lbl_count = QtWidgets.QLabel("")
        self.lbl_count.setObjectName("muted")
        filters_row.addWidget(self.lbl_count)
        layout.addLayout(filters_row)

        self.table = make_table(["Τίτλος", "Συγγραφέας", "Αριθμός", "ISBN", "Αντίτυπα", "Διαθέσιμα",
                                 "Τοποθεσία", "Κατηγορίες", "Έτος"])
        self.table.hideColumn(2)
        self.table.doubleClicked.connect(self._edit_selected)
        layout.addWidget(self.table, 1)

        for cmb in (self.cmb_library, self.cmb_category, self.cmb_shelf, self.cmb_tag):
            cmb.currentIndexChanged.connect(self.refresh)

        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(8)
        btn_add = QtWidgets.QPushButton(" Προσθήκη βιβλίου")
        btn_add.setIcon(make_icon("add", "#ffffff", 18))
        btn_add.setObjectName("success")
        btn_add.clicked.connect(self._add)
        buttons.addWidget(btn_add)
        btn_edit = QtWidgets.QPushButton(" Επεξεργασία")
        btn_edit.setIcon(make_icon("edit", "#ffffff", 18))
        btn_edit.clicked.connect(self._edit_selected)
        buttons.addWidget(btn_edit)
        btn_delete = QtWidgets.QPushButton(" Διαγραφή")
        btn_delete.setIcon(make_icon("delete", "#ffffff", 18))
        btn_delete.setObjectName("danger")
        btn_delete.clicked.connect(self._delete_selected)
        buttons.addWidget(btn_delete)
        btn_loan = QtWidgets.QPushButton(" Δανεισμός")
        btn_loan.setIcon(make_icon("loan", "#ffffff", 18))
        btn_loan.clicked.connect(self._loan_selected)
        buttons.addWidget(btn_loan)
        btn_print = QtWidgets.QPushButton(" Εκτύπωση ετικετών")
        btn_print.setIcon(make_icon("print", "#ffffff", 18))
        btn_print.clicked.connect(self._print_labels)
        buttons.addWidget(btn_print)
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

    def _reload_filters(self):
        current = {k: cmb.currentData() for k, cmb in (
            ("library", self.cmb_library), ("category", self.cmb_category),
            ("shelf", self.cmb_shelf), ("tag", self.cmb_tag))}
        self.cmb_library.blockSignals(True)
        self.cmb_category.blockSignals(True)
        self.cmb_shelf.blockSignals(True)
        self.cmb_tag.blockSignals(True)
        self.cmb_library.clear()
        self.cmb_library.addItem("Όλες οι βιβλιοθήκες", None)
        for lib in self.db.list_libraries():
            self.cmb_library.addItem(lib["name"], lib["id"])
        self.cmb_category.clear()
        self.cmb_category.addItem("Όλες οι κατηγορίες", None)
        for c in self.db.list_categories():
            self.cmb_category.addItem(f"{c['name']} ({c['cnt']})", c["id"])
        self.cmb_shelf.clear()
        self.cmb_shelf.addItem("Όλα τα ράφια", None)
        for s in self.db.list_shelves():
            self.cmb_shelf.addItem("  " * s["level"] + s["name"], s["id"])
        self.cmb_tag.clear()
        self.cmb_tag.addItem("Όλες οι ετικέτες", None)
        for t in self.db.list_common_tags():
            self.cmb_tag.addItem(f"{t['tag']} ({t['cnt']})", t["tag"])
        for k, cmb in (("library", self.cmb_library), ("category", self.cmb_category),
                       ("shelf", self.cmb_shelf), ("tag", self.cmb_tag)):
            idx = cmb.findData(current[k])
            if idx >= 0:
                cmb.setCurrentIndex(idx)
        self.cmb_library.blockSignals(False)
        self.cmb_category.blockSignals(False)
        self.cmb_shelf.blockSignals(False)
        self.cmb_tag.blockSignals(False)

    def refresh(self):
        self._reload_filters()
        self._filters = {
            "library_id": self.cmb_library.currentData(),
            "category_id": self.cmb_category.currentData(),
            "shelf_id": self.cmb_shelf.currentData(),
            "tag": self.cmb_tag.currentData(),
        }
        rows = self.db.search_books(self.search.text(), **self._filters)
        fill_table(self.table, rows, ["title", "author", "book_number", "isbn", "copies",
                                      "available", "shelves", "categories", "year"])
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 5)
            data = item.data(QtCore.Qt.UserRole)
            if data and data.get("available", 0) <= 0:
                for c in range(self.table.columnCount()):
                    self.table.item(r, c).setBackground(QtGui.QBrush(QtGui.QColor("#fdecea")))
        self.lbl_count.setText(f"{len(rows)} αποτελέσματα")

    def _selected_rows(self):
        return selected_data(self.table)

    def _add(self):
        dlg = BookDialog(self.db, self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = getattr(dlg, "_data")
            if self.db.find_duplicate(data["title"], data["isbn"]):
                ret = QtWidgets.QMessageBox.question(
                    self, "Πιθανό διπλότυπο",
                    "Παρόμοιο βιβλίο υπάρχει ήδη στον κατάλογο.\nΘέλετε να το προσθέσετε ούτως ή άλλως;")
                if ret != QtWidgets.QMessageBox.Yes:
                    return
            res = self.db.add_book(data)
            if res.get("ok"):
                self.main.status_message("Το βιβλίο προστέθηκε.")
            else:
                QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
            self.refresh()

    def _edit_selected(self):
        rows = self._selected_rows()
        if not rows:
            QtWidgets.QMessageBox.information(self, "Βιβλία", "Επιλέξτε πρώτα ένα βιβλίο.")
            return
        book = rows[0]
        dlg = BookDialog(self.db, self, book=book)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            data = getattr(dlg, "_data")
            self.db.update_book(book["id"], data)
            self.main.status_message("Οι αλλαγές αποθηκεύτηκαν.")
            self.refresh()

    def _delete_selected(self):
        rows = self._selected_rows()
        if not rows:
            QtWidgets.QMessageBox.information(self, "Βιβλία", "Επιλέξτε πρώτα βιβλία.")
            return
        ret = QtWidgets.QMessageBox.question(
            self, "Διαγραφή",
            f"Διαγραφή {len(rows)} βιβλίου/ων και του ιστορικού δανεισμού τους;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        for b in rows:
            self.db.delete_book(b["id"])
        self.main.status_message(f"Διαγράφηκαν {len(rows)} βιβλία.")
        self.refresh()

    def _loan_selected(self):
        rows = self._selected_rows()
        book = rows[0] if rows else None
        dlg = LoanDialog(self.db, self, book=book, due_days=self.main.settings.due_days)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            member = getattr(dlg, "_member")
            b = getattr(dlg, "_book")
            active = self.db.member_active_loans(member["id"])
            if len(active) >= self.main.settings.max_loans:
                QtWidgets.QMessageBox.warning(
                    self, "Όριο δανεισμού",
                    f"Το μέλος έχει φτάσει το όριο δανεισμού ({self.main.settings.max_loans} βιβλία).")
                return
            res = self.db.loan_book(b["id"], member["id"], due_days=getattr(dlg, "_days"),
                                    operator="")
            if res.get("ok"):
                self.main.status_message(f"Δανεισμός ολοκληρώθηκε, προθεσμία {res['due_date']}.")
            else:
                QtWidgets.QMessageBox.warning(self, "Σφάλμα", res.get("error", ""))
            self.refresh()
            self.main.refresh_pages()

    def _print_labels(self):
        rows = self._selected_rows()
        if not rows:
            rows = self.db.search_books(self.search.text(), **self._filters)
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εκτύπωση", "Δεν υπάρχουν βιβλία για εκτύπωση.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Αποθήκευση ετικετών", "etiketas_vivliwn.pdf",
                                                        "PDF (*.pdf)")
        if not path:
            return
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        school = self.main.settings.school_name
        book_labels_pdf(rows, path, school_name=school)
        self.main.status_message(f"Δημιουργήθηκαν {len(rows)} ετικέτες: {path}")

    def _export(self):
        rows = self.db.search_books(self.search.text(), **self._filters)
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν βιβλία προς εξαγωγή.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Εξαγωγή βιβλίων", "vivlia.xlsx",
            "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        columns = ["book_number", "title", "author", "publisher", "edition", "year", "pages",
                   "isbn", "dewey", "copies", "categories", "tags", "shelves"]
        data = [dict(b) for b in rows]
        exporter.export_rows(data, columns, path, fmt=fmt, title="Βιβλία",
                             school_name=self.main.settings.school_name)
        self.main.status_message(f"Εξήχθησαν {len(rows)} βιβλία.")