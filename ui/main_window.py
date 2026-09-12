import os
from PySide6 import QtCore, QtGui, QtWidgets

from core.db import LibraryDB
from core.settings import AppSettings
from core.backup import auto_backup
from core import paths
from services import exporter
from ui import theme
from ui.icons import make_icon
from ui.widgets.nav_button import NavButton
from ui.pages.dashboard_page import DashboardPage
from ui.pages.books_page import BooksPage
from ui.pages.members_page import MembersPage
from ui.pages.loans_page import LoansPage
from ui.pages.calendar_page import CalendarPage
from ui.pages.organize_page import OrganizePage
from ui.pages.settings_page import SettingsPage
from ui.pages.import_page import ImportPage

PAGES = [
    ("dashboard", "Αρχική", "home"),
    ("books", "Βιβλία", "book"),
    ("members", "Μέλη", "users"),
    ("loans", "Δάνεια", "loan"),
    ("calendar", "Ημερολόγιο", "calendar"),
    ("organize", "Οργάνωση", "organize"),
    ("settings", "Ρυθμίσεις", "settings"),
]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db_path):
        super().__init__()
        self.db = LibraryDB(db_path)
        self.settings = AppSettings(self.db)
        self.setWindowTitle("SchoolLIB - Διαχείριση Σχολικής Βιβλιοθήκης")
        icon = os.path.join(paths.BASE, "icon.png")
        if os.path.exists(icon):
            self.setWindowIcon(QtGui.QIcon(icon))
        self.resize(1360, 860)
        self._build_ui()
        self.apply_font_size()
        self.pages["dashboard"].refresh()
        self.showMaximized()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self.root_layout = QtWidgets.QHBoxLayout(central)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self.sidebar = QtWidgets.QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        self.sidebar.setStyleSheet(f"""
            QWidget#sidebar {{
                background: {theme.SIDEBAR};
                border-right: 1px solid #151f2a;
            }}
            QLabel#logo {{
                color: white;
                font-size: 22px;
                font-weight: 800;
                padding: 24px 20px 4px 20px;
                letter-spacing: 1px;
            }}
            QLabel#sub {{
                color: #6b7f94;
                padding: 0 20px 6px 20px;
                font-size: 11px;
                font-weight: 500;
            }}
            QFrame#separator {{
                background: #2a3b52;
                max-height: 1px;
                margin: 8px 20px;
            }}
            QPushButton#statsBtn {{
                background: transparent;
                color: #6b7f94;
                border: none;
                text-align: left;
                padding: 14px 18px 14px 14px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                margin: 2px 8px;
            }}
            QPushButton#statsBtn:hover {{
                background: #263a50;
                color: #d8e2ec;
            }}
        """)
        sb = QtWidgets.QVBoxLayout(self.sidebar)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        logo = QtWidgets.QLabel("SchoolLIB")
        logo.setObjectName("logo")
        sb.addWidget(logo)
        sub = QtWidgets.QLabel("Βιβλιοθήκη Σχολείου")
        sub.setObjectName("sub")
        sb.addWidget(sub)

        sep1 = QtWidgets.QFrame()
        sep1.setObjectName("separator")
        sep1.setFrameShape(QtWidgets.QFrame.HLine)
        sb.addWidget(sep1)

        self.nav_buttons = {}
        for key, title, icon_name in PAGES:
            btn = NavButton(title, icon_name)
            btn.clicked.connect(lambda _=False, k=key: self.show_page(k))
            sb.addWidget(btn)
            self.nav_buttons[key] = btn
        sb.addStretch()

        sep2 = QtWidgets.QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QtWidgets.QFrame.HLine)
        sb.addWidget(sep2)

        stats_btn = QtWidgets.QPushButton("  Στατιστικά")
        stats_btn.setObjectName("statsBtn")
        stats_btn.setIcon(make_icon("chart", "#6b7f94", 20))
        stats_btn.setIconSize(QtCore.QSize(20, 20))
        stats_btn.setCursor(QtCore.Qt.PointingHandCursor)
        stats_btn.clicked.connect(self.show_stats_dialog)
        sb.addWidget(stats_btn)
        sb.addSpacing(12)

        sep3 = QtWidgets.QFrame()
        sep3.setObjectName("separator")
        sep3.setFrameShape(QtWidgets.QFrame.HLine)
        sb.addWidget(sep3)

        copyright_label = QtWidgets.QLabel("Copyright \u00a9 Andreas Agouridis")
        copyright_label.setAlignment(QtCore.Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #4a5c6e; font-size: 10px; padding: 4px 10px; background: transparent; border: none;")
        sb.addWidget(copyright_label)

        website_label = QtWidgets.QLabel('<a href="https://apps.andreasagouridis.com/schoollib" style="color: #5a8ab5; text-decoration: none; font-size: 10px;">Official Web Site</a>')
        website_label.setAlignment(QtCore.Qt.AlignCenter)
        website_label.setOpenExternalLinks(True)
        website_label.setStyleSheet("color: #5a8ab5; font-size: 10px; padding: 2px 10px 10px 10px; background: transparent; border: none;")
        sb.addWidget(website_label)

        self.root_layout.addWidget(self.sidebar)

        self.stack = QtWidgets.QStackedWidget()
        self.pages = {}
        self.pages["dashboard"] = DashboardPage(self.db, self)
        self.pages["books"] = BooksPage(self.db, self)
        self.pages["members"] = MembersPage(self.db, self)
        self.pages["loans"] = LoansPage(self.db, self)
        self.pages["calendar"] = CalendarPage(self.db, self)
        self.pages["organize"] = OrganizePage(self.db, self)
        self.pages["settings"] = SettingsPage(self.db, self)
        self.pages["import"] = ImportPage(self.db, self)
        for key, _, _ in PAGES:
            self.stack.addWidget(self.pages[key])
        self.import_page = self.pages["import"]
        self.root_layout.addWidget(self.stack, 1)

        self.status = self.statusBar()
        self.status.showMessage("Έτοιμο", 3000)
        self.status.setStyleSheet("QStatusBar { color: #6b7a86; font-size: 11px; }")
        self.status.setSizeGripEnabled(False)

    def show_page(self, key):
        self.stack.setCurrentWidget(self.pages[key])
        for k, b in self.nav_buttons.items():
            b.setChecked(k == key)
        if key == "import":
            self.pages["import"].refresh()
        else:
            self.pages[key].refresh()

    def goto_import(self):
        self.show_page("import")

    def refresh_pages(self):
        for key in ("dashboard", "books", "members", "loans", "calendar", "organize"):
            try:
                self.pages[key].refresh()
            except Exception:
                pass

    def status_message(self, msg, timeout=6000):
        self.status.showMessage(msg, timeout)

    def apply_font_size(self):
        key = self.settings.font_size
        style = theme.build_stylesheet(key)
        QtWidgets.QApplication.instance().setStyleSheet(style)

    def current_page_key(self):
        w = self.stack.currentWidget()
        for k, p in self.pages.items():
            if p is w:
                return k
        return "dashboard"

    # ---- quick actions used by pages ---------------------------------
    def open_loan_dialog(self):
        self.show_page("loans")
        self.pages["loans"]._new_loan()

    def open_add_book(self):
        self.show_page("books")
        self.pages["books"]._add()

    def open_add_member(self):
        self.show_page("members")
        self.pages["members"]._add()

    def show_reminders(self):
        self.show_page("loans")
        self.pages["loans"].tabs.setCurrentIndex(0)
        self.pages["loans"]._print_reminders()

    def download_template_books(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Πρότυπο", "ypodeigma_vivliwn.xlsx",
                                                        "Excel (*.xlsx)")
        if path:
            exporter.export_rows([["B001", "Το Δέντρο", "Νίκος Παπαδόπουλος", "Εκδόσεις Αθήνα",
                                   "1η", "2020", 120, "9789600000001", "889", 2, "Λογοτεχνία",
                                   "ελληνική, μυθιστόρημα", "Ράφι 1"]],
                                 ["book_number", "title", "author", "publisher", "edition", "year",
                                  "pages", "isbn", "dewey", "copies", "categories", "tags", "shelves"],
                                 path, fmt="xlsx", title="Πρότυπο Βιβλίων")
            self.status_message("Το πρότυπο αποθηκεύτηκε.")

    def export_all_books(self):
        rows = self.db.export_all_books()
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν βιβλία.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Εξαγωγή καταλόγου", "plhrhs_katalogos.xlsx",
                                                        "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        columns = ["book_number", "title", "author", "publisher", "edition", "year", "pages",
                   "isbn", "dewey", "copies", "categories", "tags", "shelves"]
        exporter.export_rows(rows, columns, path, fmt=fmt, title="Πλήρης Κατάλογος",
                             school_name=self.settings.school_name)
        self.status_message(f"Ο πλήρης κατάλογος εξήχθη: {path}")

    def show_stats_dialog(self):
        s = self.db.stats()
        top = self.db.top_books(5)
        text = ("ΣΥΝΟΠΤΙΚΑ ΣΤΑΤΙΣΤΙΚΑ\n\n"
                f"Βιβλιοθήκες: {s['libraries']}\n"
                f"Βιβλία (τίτλοι): {s['books']}\n"
                f"Αντίτυπα: {s['copies']}\n"
                f"Μέλη: {s['members']}\n"
                f"Ράφια/τοποθεσίες: {s['shelves']}\n"
                f"Κατηγορίες: {s['categories']}\n"
                f"Ενεργά δάνεια: {s['active_loans']}\n"
                f"Συνολικοί δανεισμοί: {s['loans_total']}\n"
                f"Καθυστερημένα: {s['overdue']}\n"
                f"Λήγουν άμεσα: {s['due_soon']}\n\n"
                "ΔΗΜΟΦΙΛΕΣΤΕΡΑ ΒΙΒΛΙΑ\n")
        if top:
            for i, t in enumerate(top, 1):
                text += f"\n{i}. {t['title']} - {t['times']} δανεισμοί"
        else:
            text += "\n- Κανένα δάνειο ακόμη -"
        QtWidgets.QMessageBox.information(self, "Στατιστικά", text)

    # ---- backup dir / temp -------------------------------------------
    def backup_dir(self):
        from core.paths import backups_dir
        return backups_dir()

    def tmp_path(self, name):
        from core.paths import data_dir
        return data_dir(name)

    def closeEvent(self, event):
        try:
            if self.settings.auto_backup:
                pwd = self.settings.backup_password or None
                auto_backup(self.db.path, self.backup_dir(),
                            keep=self.settings.backup_count, password=pwd)
        except Exception:
            pass
        event.accept()