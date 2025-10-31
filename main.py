import sys, os, datetime, csv, webbrowser
from PySide6 import QtCore, QtGui, QtWidgets
from db import LibraryDB
from utils import generate_qr_png, export_books_pdf_labels, encrypt_backup

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "library.db")

class BookItemWidget(QtWidgets.QWidget):
    def __init__(self, book, parent=None, delete_callback=None, click_callback=None):
        super().__init__(parent)
        self.book = book
        self.delete_callback = delete_callback
        self.click_callback = click_callback
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        lbl = QtWidgets.QLabel(f"{book['title']} — {book['author']} [{book['book_number']}]")
        layout.addWidget(lbl)

        btn_google = QtWidgets.QPushButton("🔍")
        btn_google.setMaximumWidth(30)
        btn_google.setToolTip("Search Google")
        btn_google.clicked.connect(lambda: webbrowser.open(f"https://www.google.com/search?q={book['title']}"))
        layout.addWidget(btn_google)

        btn_delete = QtWidgets.QPushButton("🗑️")
        btn_delete.setMaximumWidth(30)
        btn_delete.setToolTip("Διαγραφή βιβλίου")
        btn_delete.clicked.connect(lambda: self.delete_callback(self.book) if self.delete_callback else None)
        layout.addWidget(btn_delete)

class MemberItemWidget(QtWidgets.QWidget):
    def __init__(self, member, delete_callback=None):
        super().__init__()
        self.member = member
        self.delete_callback = delete_callback
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        member_dict = dict(member)
        lbl = QtWidgets.QLabel(f"{member_dict['name']} [{member_dict['member_number']}] | {member_dict.get('class','')}")
        layout.addWidget(lbl)

        btn_delete = QtWidgets.QPushButton("🗑️")
        btn_delete.setMaximumWidth(30)
        btn_delete.clicked.connect(lambda: self.delete_callback(member) if self.delete_callback else None)
        layout.addWidget(btn_delete)
        layout.addStretch()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(BASE, "icon.png") 
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.setWindowTitle("SchoolLIB - Andreas Agouridis")
        self.resize(1300,800)
        self.db = LibraryDB(DB)
        self._build_ui()
        self.load_sidebar()
        self.load_members_list()

    def _build_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        h = QtWidgets.QHBoxLayout(central)

        sidebar = QtWidgets.QWidget()
        sidebar.setMinimumWidth(500)
        s_layout = QtWidgets.QVBoxLayout(sidebar)
        self.sidebar_search = QtWidgets.QLineEdit()
        self.sidebar_search.setPlaceholderText("Φίλτρο τίτλου ή συγγραφέα")
        self.sidebar_search.returnPressed.connect(self.load_sidebar)
        s_layout.addWidget(self.sidebar_search)

        self.book_list = QtWidgets.QListWidget()
        self.book_list.setMinimumHeight(600)
        s_layout.addWidget(self.book_list)

        btn_refresh = QtWidgets.QPushButton("Ανανέωση")
        btn_refresh.clicked.connect(self.load_sidebar)
        s_layout.addWidget(btn_refresh)

        btn_delete_books = QtWidgets.QPushButton("Διαγραφή όλων των βιβλίων")
        btn_delete_books.clicked.connect(self.delete_all_books)
        s_layout.addWidget(btn_delete_books)

        btn_delete_members = QtWidgets.QPushButton("Διαγραφή όλων των μελών")
        btn_delete_members.clicked.connect(self.delete_all_members)
        s_layout.addWidget(btn_delete_members)

        h.addWidget(sidebar)

        main = QtWidgets.QWidget()
        m_layout = QtWidgets.QVBoxLayout(main)

        header_label = QtWidgets.QLabel("SchoolLIB")
        header_label.setAlignment(QtCore.Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 32pt; font-weight: bold; color: #2c3e50;")
        m_layout.addWidget(header_label)

        controls = QtWidgets.QHBoxLayout()
        self.q_search = QtWidgets.QLineEdit()
        self.q_search.setPlaceholderText("Αναζήτηση τίτλου, συγγραφέα ή ISBN")
        controls.addWidget(self.q_search)
        btn_search = QtWidgets.QPushButton("Αναζήτηση")
        btn_search.clicked.connect(self.search)
        controls.addWidget(btn_search)
        btn_export = QtWidgets.QPushButton("Εξαγωγή CSV")
        btn_export.clicked.connect(self.export_csv)
        controls.addWidget(btn_export)
        btn_backup = QtWidgets.QPushButton("Κρυπτογραφημένο Backup")
        btn_backup.clicked.connect(self.do_backup)
        controls.addWidget(btn_backup)
        btn_stats = QtWidgets.QPushButton("Στατιστικά")
        btn_stats.clicked.connect(self.show_stats)
        controls.addWidget(btn_stats)
        btn_loans = QtWidgets.QPushButton("Ενεργά Δάνεια")
        btn_loans.clicked.connect(self.show_active_loans)
        controls.addWidget(btn_loans)

        btn_import_books = QtWidgets.QPushButton("Import Books")
        btn_import_books.clicked.connect(self.import_books)
        controls.addWidget(btn_import_books)
        btn_import_members = QtWidgets.QPushButton("Import Members")
        btn_import_members.clicked.connect(self.import_members)
        controls.addWidget(btn_import_members)

        m_layout.addLayout(controls)

        self.results_area = QtWidgets.QListWidget()
        m_layout.addWidget(self.results_area,5)

        form = QtWidgets.QWidget()
        f_layout = QtWidgets.QHBoxLayout(form)

        gb = QtWidgets.QGroupBox("Προσθήκη βιβλίου")
        gbl = QtWidgets.QFormLayout(gb)
        self.input_book_number = QtWidgets.QLineEdit(); gbl.addRow("Αρ. Βιβλίου", self.input_book_number)
        self.input_title = QtWidgets.QLineEdit(); gbl.addRow("Τίτλος", self.input_title)
        self.input_author = QtWidgets.QLineEdit(); gbl.addRow("Συγγραφέας", self.input_author)
        self.input_isbn = QtWidgets.QLineEdit(); gbl.addRow("ISBN", self.input_isbn)
        self.input_copies = QtWidgets.QSpinBox(); self.input_copies.setValue(1); gbl.addRow("Αντίτυπα", self.input_copies)
        btn_add_book = QtWidgets.QPushButton("Προσθήκη"); btn_add_book.clicked.connect(self.add_book)
        gbl.addRow(btn_add_book)
        f_layout.addWidget(gb)

        gm = QtWidgets.QGroupBox("Προσθήκη μέλους")
        gml = QtWidgets.QFormLayout(gm)
        self.input_member_number = QtWidgets.QLineEdit(); gml.addRow("Αρ. Μέλους", self.input_member_number)
        self.input_member_name = QtWidgets.QLineEdit(); gml.addRow("Όνομα", self.input_member_name)
        self.input_member_class = QtWidgets.QLineEdit(); gml.addRow("Τάξη", self.input_member_class)
        btn_add_member = QtWidgets.QPushButton("Προσθήκη"); btn_add_member.clicked.connect(self.add_member)
        gml.addRow(btn_add_member)
        f_layout.addWidget(gm)

        m_layout.addWidget(form,2)

        self.members_list = QtWidgets.QListWidget()
        m_layout.addWidget(QtWidgets.QLabel("Μέλη:"),0)
        m_layout.addWidget(self.members_list,1)

        footer = QtWidgets.QWidget()
        footer_layout = QtWidgets.QHBoxLayout(footer)
        footer_layout.setContentsMargins(10,5,10,5)
        copyright_label = QtWidgets.QLabel("© Andreas Agouridis")
        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()
        btn_site = QtWidgets.QPushButton("Visit Website")
        btn_site.setStyleSheet("padding:5px; font-weight:bold;")
        btn_site.clicked.connect(lambda: webbrowser.open("https://schoollib.ct.ws"))
        footer_layout.addWidget(btn_site)
        m_layout.addWidget(footer)

        h.addWidget(main,3)
        self.status = self.statusBar()

    def load_sidebar(self):
        q = self.sidebar_search.text().strip().lower()
        books = self.db.list_books_alpha(limit=200)
        self.book_list.clear()
        for b in books:
            if q and q not in (b['title'] or "").lower() and q not in (b['author'] or "").lower():
                continue
            item = QtWidgets.QListWidgetItem()
            widget = BookItemWidget(b, delete_callback=self.delete_book, click_callback=self.open_book_dialog)
            item.setSizeHint(widget.sizeHint())
            self.book_list.addItem(item)
            self.book_list.setItemWidget(item, widget)
            widget.mousePressEvent = lambda e, bk=b: self.open_book_dialog(bk)

    def load_members_list(self):
        self.members_list.clear()
        conn = self.db._conn()
        rows = conn.cursor().execute("SELECT * FROM members").fetchall()
        for m in rows:
            item = QtWidgets.QListWidgetItem()
            widget = MemberItemWidget(m, delete_callback=self.delete_member)
            item.setSizeHint(widget.sizeHint())
            self.members_list.addItem(item)
            self.members_list.setItemWidget(item, widget)
        conn.close()

    def delete_all_books(self):
        if QtWidgets.QMessageBox.question(self,"Confirm","Διαγραφή όλων των βιβλίων και δανείων;") == QtWidgets.QMessageBox.Yes:
            conn = self.db._conn()
            conn.execute("DELETE FROM loans")
            conn.execute("DELETE FROM books")
            conn.commit(); conn.close()
            self.load_sidebar()

    def delete_all_members(self):
        if QtWidgets.QMessageBox.question(self,"Confirm","Διαγραφή όλων των μελών;") == QtWidgets.QMessageBox.Yes:
            conn = self.db._conn()
            conn.execute("DELETE FROM members")
            conn.commit(); conn.close()
            self.load_members_list()

    def delete_book(self, book):
        if QtWidgets.QMessageBox.question(self,"Confirm",f"Διαγραφή βιβλίου {book['title']}?") == QtWidgets.QMessageBox.Yes:
            conn = self.db._conn()
            conn.execute("DELETE FROM loans WHERE book_id=?", (book['BookID'],))
            conn.execute("DELETE FROM books WHERE BookID=?", (book['BookID'],))
            conn.commit(); conn.close()
            self.load_sidebar()

    def delete_member(self, member):
        member_dict = dict(member)
        if QtWidgets.QMessageBox.question(self,"Confirm",f"Διαγραφή μέλους {member_dict['name']}?") == QtWidgets.QMessageBox.Yes:
            conn = self.db._conn()
            conn.execute("DELETE FROM members WHERE MemberID=?", (member_dict['MemberID'],))
            conn.commit(); conn.close()
            self.load_members_list()

    def open_book_dialog(self,b):
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle(b['title']); dlg.resize(500,400)
        layout = QtWidgets.QVBoxLayout(dlg)
        layout.addWidget(QtWidgets.QLabel(f"<b>{b['title']}</b><br>{b['author']}<br>ISBN: {b.get('isbn','')}<br>Αντίτυπα: {b.get('copies',1)}"))

        members = self.db._conn().cursor().execute("SELECT MemberID, name FROM members").fetchall()
        member_dropdown = QtWidgets.QComboBox(); member_dropdown.addItem("---Επιλέξτε Μέλος---", None)
        for m in members:
            member_dropdown.addItem(f"{m['name']} ({m['MemberID']})", m['MemberID'])
        layout.addWidget(member_dropdown)
        btn_loan = QtWidgets.QPushButton("Δάνεισε")
        def do_loan():
            member_id = member_dropdown.currentData()
            if not member_id:
                QtWidgets.QMessageBox.warning(dlg,"Error","Επίλεξε μέλος")
                return
            res = self.db.loan_book(b['BookID'], member_id)
            if res.get('ok'):
                QtWidgets.QMessageBox.information(dlg,"ΟΚ",f"Το Βιβλίο δανείστηκε.")
            else:
                QtWidgets.QMessageBox.warning(dlg,"Σφάλμα", res.get('error','Άγνωστο σφάλμα'))
        btn_loan.clicked.connect(do_loan)
        layout.addWidget(btn_loan)

        loans = self.db.list_active_loans()
        loan_dropdown = QtWidgets.QComboBox(); loan_dropdown.addItem("---Επιλέξτε Δάνειο---", None)
        for l in loans:
            loan_dropdown.addItem(f"{l['LoanID']}: {l['book_title']} σε {l['member_name']}", l['LoanID'])
        layout.addWidget(loan_dropdown)
        btn_return = QtWidgets.QPushButton("Επιστροφή")
        def do_return():
            loan_id = loan_dropdown.currentData()
            if not loan_id:
                QtWidgets.QMessageBox.warning(dlg,"Error","Επίλεξε δάνειο")
                return
            res = self.db.return_book(loan_id)
            if res.get('ok'):
                QtWidgets.QMessageBox.information(dlg,"ΟΚ","Το βιβλίο επιστράφηκε")
            else:
                QtWidgets.QMessageBox.warning(dlg,"Σφάλμα",res.get('error','Άγνωστο σφάλμα'))
        btn_return.clicked.connect(do_return)
        layout.addWidget(btn_return)

        dlg.exec_()

    def search(self):
        q = self.q_search.text().strip()
        results = self.db.search_books(q)
        self.results_area.clear()
        for b in results:
            item = QtWidgets.QListWidgetItem(f"{b['title']} — {b['author']} [{b['book_number']}]")
            item.setData(QtCore.Qt.UserRole, b)
            self.results_area.addItem(item)
        self.status.showMessage(f"Αποτελέσματα: {len(results)}", 5000)

    def add_book(self):
        num = self.input_book_number.text().strip() or f"B{int(datetime.datetime.now().timestamp())%100000}"
        title = self.input_title.text().strip(); author = self.input_author.text().strip(); isbn = self.input_isbn.text().strip(); copies = self.input_copies.value()
        res = self.db.add_book(num,title,author,isbn,"Main",copies)
        if res.get('error'):
            QtWidgets.QMessageBox.warning(self,"Error",res['error'])
        else:
            QtWidgets.QMessageBox.information(self,"Added","Βιβλίο προστέθηκε")
            self.load_sidebar()

    def add_member(self):
        num = self.input_member_number.text().strip() or f"M{int(datetime.datetime.now().timestamp())%100000}"
        name = self.input_member_name.text().strip(); cls = self.input_member_class.text().strip()
        res = self.db.add_member(num,name,cls)
        if res.get('error'):
            QtWidgets.QMessageBox.warning(self,"Error",res['error'])
        else:
            QtWidgets.QMessageBox.information(self,"Added","Μέλος προστέθηκε")
            self.load_members_list()

    def import_books(self):
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,"Open CSV","*.csv")
        if not path: return
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                book_number = row.get('book_number') or f"B{int(datetime.datetime.now().timestamp())%100000}"
                title = row.get('title','')
                author = row.get('author','')
                isbn = row.get('isbn','')
                location = row.get('location','Main')
                copies = int(row.get('copies',1))
                self.db.add_book(book_number,title,author,isbn,location,copies)
        self.load_sidebar()
        QtWidgets.QMessageBox.information(self,"Import","Τα βιβλία εισήχθησαν με επιτυχία!")

    def import_members(self):
        path,_ = QtWidgets.QFileDialog.getOpenFileName(self,"Open CSV","*.csv")
        if not path: return
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                member_number = row.get('member_number') or f"M{int(datetime.datetime.now().timestamp())%100000}"
                name = row.get('name','')
                cls = row.get('class','')
                self.db.add_member(member_number,name,cls)
        self.load_members_list()
        QtWidgets.QMessageBox.information(self,"Import","Τα μέλη εισήχθησαν με επιτυχία!")

    def export_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Save CSV","books_export.csv","CSV Files (*.csv)")
        if not path: return
        rows = self.db.export_books()
        with open(path,"w",encoding="utf-8-sig",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["book_number","title","author","isbn","location","copies"])
            for r in rows:
                writer.writerow([r['book_number'], r['title'], r['author'], r['isbn'], r.get('location',''), r.get('copies',1)])
        QtWidgets.QMessageBox.information(self,"Exported",f"CSV εξαγωγή αποθηκεύτηκε: {path}")

    def do_backup(self):
        path,_ = QtWidgets.QFileDialog.getSaveFileName(self,"Save Encrypted Backup","backup.enc","Encrypted Files (*.enc)")
        if not path: return
        pwd, ok = QtWidgets.QInputDialog.getText(self,"Password","Δώσε κωδικό για backup",QtWidgets.QLineEdit.Password)
        if not ok or not pwd: return
        encrypt_backup(DB,path,pwd)
        QtWidgets.QMessageBox.information(self,"Done",f"Κρυπτογραφημένο backup αποθηκεύτηκε: {path}")

    def show_stats(self):
        s = self.db.stats()
        msg = f"Βιβλία: {s['total_books']}\nΜέλη: {s['total_members']}\nΕνεργά Δάνεια: {s['active_loans']}\nTop: {', '.join([t['title']+'('+str(t['times'])+')' for t in s['top']])}"
        QtWidgets.QMessageBox.information(self,"Stats",msg)

    def show_active_loans(self):
        loans = self.db.list_active_loans()
        dlg = QtWidgets.QDialog(self); dlg.setWindowTitle("Ενεργά Δάνεια"); dlg.resize(600,400)
        layout = QtWidgets.QVBoxLayout(dlg)
        lw = QtWidgets.QListWidget()
        for l in loans:
            lw.addItem(f"LoanID {l['LoanID']} — {l['book_title']} σε {l['member_name']} | Δανείστηκε: {l['loan_date']} | Προθεσμία: {l['due_date']}")
        layout.addWidget(lw)
        dlg.exec_()

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(); w.show(); sys.exit(app.exec())

if __name__ == '__main__':
    main()
