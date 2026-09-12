from PySide6 import QtCore, QtWidgets

from ui.icons import make_icon
from ui.widgets.table_helpers import make_table, fill_table, selected_data, SearchBar


class OrganizePage(QtWidgets.QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.setObjectName("page")
        self._current_library = None
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        header = QtWidgets.QLabel("Οργάνωση - Φάκελοι")
        header.setObjectName("header")
        layout.addWidget(header)
        hint = QtWidgets.QLabel("Δημιουργήστε βιβλιοθήκες, ράφια (αίθουσα, ντουλάπα, ράφι) και "
                                "κατηγορίες. Αναθέστε βιβλία στα ράφια μαζικά.", objectName="muted")
        layout.addWidget(hint)

        main_w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(main_w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(14)

        left = QtWidgets.QWidget()
        lv = QtWidgets.QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(12)

        lib_group = QtWidgets.QGroupBox("Βιβλιοθήκες")
        lg = QtWidgets.QVBoxLayout(lib_group)
        lib_row = QtWidgets.QHBoxLayout()
        self.cmb_lib = QtWidgets.QComboBox()
        self.cmb_lib.currentIndexChanged.connect(self._on_library_changed)
        lib_row.addWidget(self.cmb_lib, 1)
        btn_lib_add = QtWidgets.QPushButton("Προσθήκη")
        btn_lib_add.clicked.connect(self._add_library)
        lib_row.addWidget(btn_lib_add)
        btn_lib_edit = QtWidgets.QPushButton("Μετονομασία")
        btn_lib_edit.clicked.connect(self._rename_library)
        lib_row.addWidget(btn_lib_edit)
        btn_lib_del = QtWidgets.QPushButton("-")
        btn_lib_del.setObjectName("danger")
        btn_lib_del.clicked.connect(self._delete_library)
        lib_row.addWidget(btn_lib_del)
        lg.addLayout(lib_row)
        lv.addWidget(lib_group)

        shelf_group = QtWidgets.QGroupBox("Ράφια και Τοποθεσίες")
        sg = QtWidgets.QVBoxLayout(shelf_group)
        self.tree_shelves = QtWidgets.QTreeWidget()
        self.tree_shelves.setHeaderLabels(["Τοποθεσία", "Βιβλία"])
        self.tree_shelves.setColumnWidth(0, 220)
        self.tree_shelves.itemSelectionChanged.connect(self._update_shelf_actions)
        sg.addWidget(self.tree_shelves, 1)
        shelf_row = QtWidgets.QHBoxLayout()
        btn_shelf_add = QtWidgets.QPushButton("Νέο ράφι")
        btn_shelf_add.clicked.connect(self._add_shelf)
        shelf_row.addWidget(btn_shelf_add)
        btn_shelf_edit = QtWidgets.QPushButton("Μετονομασία")
        btn_shelf_edit.clicked.connect(self._rename_shelf)
        shelf_row.addWidget(btn_shelf_edit)
        btn_shelf_del = QtWidgets.QPushButton("Διαγραφή")
        btn_shelf_del.setObjectName("danger")
        btn_shelf_del.clicked.connect(self._delete_shelf)
        shelf_row.addWidget(btn_shelf_del)
        btn_shelf_move = QtWidgets.QPushButton("Μετακίνηση")
        btn_shelf_move.clicked.connect(self._move_shelf)
        shelf_row.addWidget(btn_shelf_move)
        sg.addLayout(shelf_row)
        lv.addWidget(shelf_group, 3)

        cat_group = QtWidgets.QGroupBox("Κατηγορίες")
        cg = QtWidgets.QVBoxLayout(cat_group)
        self.list_cats = QtWidgets.QListWidget()
        cg.addWidget(self.list_cats)
        cat_row = QtWidgets.QHBoxLayout()
        self.ed_cat = QtWidgets.QLineEdit()
        self.ed_cat.setPlaceholderText("Νέα κατηγορία")
        self.ed_cat.returnPressed.connect(self._add_category)
        cat_row.addWidget(self.ed_cat, 1)
        btn_cat_add = QtWidgets.QPushButton("Προσθήκη")
        btn_cat_add.clicked.connect(self._add_category)
        cat_row.addWidget(btn_cat_add)
        btn_cat_edit = QtWidgets.QPushButton("Μετονομασία")
        btn_cat_edit.clicked.connect(self._rename_category)
        cat_row.addWidget(btn_cat_edit)
        btn_cat_del = QtWidgets.QPushButton("Διαγραφή")
        btn_cat_del.setObjectName("danger")
        btn_cat_del.clicked.connect(self._delete_category)
        cat_row.addWidget(btn_cat_del)
        cg.addLayout(cat_row)
        lv.addWidget(cat_group, 2)

        tag_group = QtWidgets.QGroupBox("Δημοφιλείς Ετικέτες")
        tg = QtWidgets.QVBoxLayout(tag_group)
        self.list_tags = QtWidgets.QListWidget()
        tg.addWidget(self.list_tags)
        lv.addWidget(tag_group, 1)

        h.addWidget(left, 2)

        right = QtWidgets.QWidget()
        rv = QtWidgets.QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        assign_group = QtWidgets.QGroupBox("Ανάθεση βιβλίων σε ράφι")
        ag = QtWidgets.QVBoxLayout(assign_group)
        self.books_search = SearchBar("Αναζήτηση βιβλίων")
        self.books_search.search_requested.connect(self._load_books)
        ag.addWidget(self.books_search)
        self.books_table = make_table(["Βιβλίο", "Συγγραφέας", "Αριθμός", "Τρέχοντα ράφια"])
        self.books_table.hideColumn(2)
        ag.addWidget(self.books_table, 1)
        assign_row = QtWidgets.QHBoxLayout()
        btn_assign = QtWidgets.QPushButton(" Ανάθεση στο επιλεγμένο ράφι")
        btn_assign.setIcon(make_icon("add", "#ffffff", 18))
        btn_assign.setObjectName("success")
        btn_assign.clicked.connect(self._assign_selected)
        assign_row.addWidget(btn_assign)
        btn_unassign = QtWidgets.QPushButton(" Απομάκρυνση από ράφι")
        btn_unassign.setIcon(make_icon("delete", "#ffffff", 18))
        btn_unassign.clicked.connect(self._unassign_selected)
        assign_row.addWidget(btn_unassign)
        btn_refresh_books = QtWidgets.QPushButton(" Ανανέωση")
        btn_refresh_books.setIcon(make_icon("refresh", "#ffffff", 18))
        btn_refresh_books.clicked.connect(self._load_books)
        assign_row.addWidget(btn_refresh_books)
        assign_row.addStretch()
        ag.addLayout(assign_row)
        rv.addWidget(assign_group, 1)

        if_group = QtWidgets.QGroupBox("Εισαγωγή / Εξαγωγή")
        ig = QtWidgets.QVBoxLayout(if_group)
        ig.addWidget(QtWidgets.QLabel(
            "Μεταφέρετε εύκολα καταλόγους από άλλα προγράμματα ή Excel. "
            "Κατεβάστε πρότυπο αρχείο, συμπληρώστε και εισάγετε.", objectName="muted"))
        ig_row = QtWidgets.QHBoxLayout()
        btn_template = QtWidgets.QPushButton(" Πρότυπο Excel")
        btn_template.setIcon(make_icon("template", "#ffffff", 18))
        btn_template.clicked.connect(self.main.download_template_books)
        ig_row.addWidget(btn_template)
        btn_open_import = QtWidgets.QPushButton(" Οδηγός Εισαγωγής")
        btn_open_import.setIcon(make_icon("import", "#ffffff", 18))
        btn_open_import.setObjectName("secondary")
        btn_open_import.clicked.connect(self.main.goto_import)
        ig_row.addWidget(btn_open_import)
        btn_export = QtWidgets.QPushButton(" Εξαγωγή πλήρους καταλόγου")
        btn_export.setIcon(make_icon("export", "#ffffff", 18))
        btn_export.clicked.connect(self.main.export_all_books)
        ig_row.addWidget(btn_export)
        ig_row.addStretch()
        ig.addLayout(ig_row)
        rv.addWidget(if_group)

        h.addWidget(right, 3)
        layout.addWidget(main_w, 1)

    def _on_library_changed(self):
        self._current_library = self.cmb_lib.currentData()
        self._load_shelves()
        self._load_books()

    def refresh(self):
        self._reload_libraries()
        self._load_categories()
        self._load_tags()
        self._load_books()

    def _reload_libraries(self):
        libs = self.db.list_libraries()
        current = self._current_library
        self.cmb_lib.blockSignals(True)
        self.cmb_lib.clear()
        for lib in libs:
            self.cmb_lib.addItem(lib["name"], lib["id"])
        self.cmb_lib.blockSignals(False)
        if current is not None:
            idx = self.cmb_lib.findData(current)
            if idx >= 0:
                self.cmb_lib.setCurrentIndex(idx)
        self._current_library = self.cmb_lib.currentData()
        self._load_shelves()

    def _load_shelves(self):
        self.tree_shelves.clear()
        shelves = self.db.list_shelves(self._current_library)
        nodes = {}
        for s in shelves:
            parent = None
            if s["parent_id"]:
                parent = nodes.get(s["parent_id"])
            item = QtWidgets.QTreeWidgetItem(parent if parent else self.tree_shelves.invisibleRootItem())
            item.setText(0, "  " * s["level"] + s["name"])
            item.setText(1, str(self.db.shelf_books_count(s["id"])))
            item.setData(0, QtCore.Qt.UserRole, s)
            nodes[s["id"]] = item
        self.tree_shelves.expandAll()
        self._update_shelf_actions()

    def _selected_shelf(self):
        items = self.tree_shelves.selectedItems()
        if not items:
            return None
        return items[0].data(0, QtCore.Qt.UserRole)

    def _add_shelf(self):
        parent = self._selected_shelf()
        name, ok = QtWidgets.QInputDialog.getText(self, "Νέο ράφι",
                                                  "Όνομα ραφιού (π.χ. Ντουλάπα 1, Ράφι 2):")
        name = name.strip()
        if not ok or not name:
            return
        self.db.add_shelf(name, parent_id=parent["id"] if parent else None,
                          library_id=self._current_library)
        self._load_shelves()

    def _rename_shelf(self):
        shelf = self._selected_shelf()
        if not shelf:
            QtWidgets.QMessageBox.information(self, "Ράφια", "Επιλέξτε πρώτα ράφι.")
            return
        name, ok = QtWidgets.QInputDialog.getText(self, "Μετονομασία", "Νέο όνομα:", text=shelf["name"])
        if ok and name.strip():
            self.db.rename_shelf(shelf["id"], name.strip())
            self._load_shelves()

    def _delete_shelf(self):
        shelf = self._selected_shelf()
        if not shelf:
            QtWidgets.QMessageBox.information(self, "Ράφια", "Επιλέξτε πρώτα ράφι.")
            return
        ret = QtWidgets.QMessageBox.question(self, "Διαγραφή",
                                             f"Διαγραφή ραφιού '{shelf['name']}' και τυχόν υποφακέλων;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        self.db.delete_shelf(shelf["id"])
        self._load_shelves()
        self._load_books()

    def _move_shelf(self):
        shelf = self._selected_shelf()
        if not shelf:
            QtWidgets.QMessageBox.information(self, "Ράφια", "Επιλέξτε πρώτα ράφι.")
            return
        items = [("(Κορυφή)", None)]
        for s in self.db.list_shelves(self._current_library):
            if s["id"] != shelf["id"]:
                items.append(("  " * s["level"] + s["name"], s["id"]))
        from PySide6.QtWidgets import QDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Μετακίνηση ραφιού")
        l = QVBoxLayout(dlg)
        l.addWidget(QLabel(f"Μετακίνηση του '{shelf['name']}' κάτω από:"))
        cmb = QComboBox()
        for txt, sid in items:
            cmb.addItem(txt, sid)
        l.addWidget(cmb)
        row = QHBoxLayout()
        cancel = QPushButton("Άκυρο"); cancel.clicked.connect(dlg.reject)
        ok = QPushButton("Μετακίνηση"); ok.setObjectName("success"); ok.clicked.connect(dlg.accept)
        row.addWidget(cancel); row.addStretch(); row.addWidget(ok)
        l.addLayout(row)
        if dlg.exec_() != QDialog.Accepted:
            return
        self.db.move_shelf(shelf["id"], cmb.currentData())
        self._load_shelves()

    def _update_shelf_actions(self):
        pass

    def _load_books(self):
        rows = self.db.search_books(self.books_search.text())
        fill_table(self.books_table, rows, ["title", "author", "book_number", "shelves"])

    def _assign_selected(self):
        shelf = self._selected_shelf()
        books = selected_data(self.books_table)
        if not shelf:
            QtWidgets.QMessageBox.information(self, "Ανάθεση", "Επιλέξτε πρώτα ένα ράφι στα αριστερά.")
            return
        if not books:
            QtWidgets.QMessageBox.information(self, "Ανάθεση", "Επιλέξτε βιβλία από τον πίνακα.")
            return
        self.db.assign_books_to_shelf([b["id"] for b in books], shelf["id"])
        self.main.status_message(f"Ανατέθηκαν {len(books)} βιβλία στο ράφι.")
        self._load_shelves()
        self._load_books()

    def _unassign_selected(self):
        shelf = self._selected_shelf()
        books = selected_data(self.books_table)
        if not shelf or not books:
            QtWidgets.QMessageBox.information(self, "Απομάκρυνση",
                                              "Επιλέξτε ράφι και βιβλία.")
            return
        for b in books:
            self.db.remove_book_from_shelf(b["id"], shelf["id"])
        self.main.status_message("Τα βιβλία απομακρύνθηκαν από το ράφι.")
        self._load_shelves()
        self._load_books()

    def _add_category(self):
        name = self.ed_cat.text().strip()
        if not name:
            return
        res = self.db.add_category(name)
        if res.get("error"):
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", res["error"])
        self.ed_cat.clear()
        self._load_categories()

    def _rename_category(self):
        item = self.list_cats.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Κατηγορίες", "Επιλέξτε κατηγορία.")
            return
        cid, name = item.data(QtCore.Qt.UserRole), item.text()
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Μετονομασία", "Νέο όνομα:", text=name)
        if ok and new_name.strip():
            self.db.rename_category(cid, new_name.strip())
            self._load_categories()

    def _delete_category(self):
        item = self.list_cats.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Κατηγορίες", "Επιλέξτε κατηγορία.")
            return
        ret = QtWidgets.QMessageBox.question(self, "Διαγραφή",
                                             f"Διαγραφή κατηγορίας '{item.text()}';")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        self.db.delete_category(item.data(QtCore.Qt.UserRole))
        self._load_categories()

    def _load_categories(self):
        self.list_cats.clear()
        for c in self.db.list_categories():
            item = QtWidgets.QListWidgetItem(f"{c['name']} ({c['cnt']})")
            item.setData(QtCore.Qt.UserRole, c["id"])
            self.list_cats.addItem(item)

    def _load_tags(self):
        self.list_tags.clear()
        for t in self.db.list_common_tags():
            self.list_tags.addItem(f"{t['tag']} ({t['cnt']})")

    def _add_library(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "Νέα βιβλιοθήκη", "Όνομα βιβλιοθήκης:")
        if ok and name.strip():
            self.db.add_library(name.strip())
            self._reload_libraries()

    def _rename_library(self):
        lib_id = self._current_library
        if not lib_id:
            return
        res = self.db.list_libraries()
        name = next((l["name"] for l in res if l["id"] == lib_id), "")
        new_name, ok = QtWidgets.QInputDialog.getText(self, "Μετονομασία", "Νέο όνομα:", text=name)
        if ok and new_name.strip():
            self.db.rename_library(lib_id, new_name.strip())
            self._reload_libraries()

    def _delete_library(self):
        lib_id = self._current_library
        if not lib_id:
            return
        ret = QtWidgets.QMessageBox.question(self, "Διαγραφή",
                                             "Διαγραφή βιβλιοθήκης και όλων των δεδομένων της;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        res = self.db.delete_library(lib_id)
        if res.get("error"):
            QtWidgets.QMessageBox.warning(self, "Σφάλμα", res["error"])
        self._reload_libraries()
        self.refresh()