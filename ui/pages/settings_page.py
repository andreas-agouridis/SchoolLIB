from PySide6 import QtCore, QtWidgets

from core import backup
from ui.icons import make_icon


class SettingsPage(QtWidgets.QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.settings = main_window.settings
        self.setObjectName("page")
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        header = QtWidgets.QLabel("Ρυθμίσεις")
        header.setObjectName("header")
        layout.addWidget(header)

        gen = QtWidgets.QGroupBox("Γενικές Ρυθμίσεις")
        gl = QtWidgets.QFormLayout(gen)
        gl.setSpacing(10)
        self.ed_school = QtWidgets.QLineEdit(self.settings.school_name)
        gl.addRow("Όνομα σχολείου / βιβλιοθήκης:", self.ed_school)
        self.sp_due = QtWidgets.QSpinBox()
        self.sp_due.setRange(1, 366)
        self.sp_due.setValue(self.settings.due_days)
        gl.addRow("Προθεσμία δανεισμού (ημέρες):", self.sp_due)
        self.sp_max = QtWidgets.QSpinBox()
        self.sp_max.setRange(1, 50)
        self.sp_max.setValue(self.settings.max_loans)
        gl.addRow("Μέγιστο δανεισμένο βιβλίων ανά μέλος:", self.sp_max)
        self.sp_remind = QtWidgets.QSpinBox()
        self.sp_remind.setRange(1, 30)
        self.sp_remind.setValue(self.settings.remind_days)
        gl.addRow("Προειδοποίηση X ημέρες πριν λήξει:", self.sp_remind)
        self.cmb_font = QtWidgets.QComboBox()
        self.cmb_font.addItem("Μεγάλα γράμματα", "large")
        self.cmb_font.addItem("Πολύ μεγάλα γράμματα", "xlarge")
        idx = self.cmb_font.findData(self.settings.font_size)
        if idx >= 0:
            self.cmb_font.setCurrentIndex(idx)
        gl.addRow("Μέγεθος γραμματοσειράς:", self.cmb_font)
        btn_general = QtWidgets.QPushButton(" Αποθήκευση γενικών ρυθμίσεων")
        btn_general.setIcon(make_icon("check", "#ffffff", 18))
        btn_general.setObjectName("success")
        btn_general.clicked.connect(self._save_general)
        gl.addRow(btn_general)
        layout.addWidget(gen)

        bk = QtWidgets.QGroupBox("Αντίγραφα ασφαλείας (Backup)")
        bl = QtWidgets.QFormLayout(bk)
        bl.setSpacing(10)
        self.chk_auto = QtWidgets.QCheckBox("Αυτόματο backup κατά το κλείσιμο")
        self.chk_auto.setChecked(self.settings.auto_backup)
        bl.addRow("", self.chk_auto)
        self.ed_bk_password = QtWidgets.QLineEdit(self.settings.backup_password)
        self.ed_bk_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ed_bk_password.setPlaceholderText("Αφήστε κενό για μη κρυπτογραφημένο backup")
        bl.addRow("Κωδικός backup:", self.ed_bk_password)
        self.sp_bk_count = QtWidgets.QSpinBox()
        self.sp_bk_count.setRange(1, 50)
        self.sp_bk_count.setValue(self.settings.backup_count)
        bl.addRow("Να διατηρούνται τα τελευταία:", self.sp_bk_count)
        btn_bk_now = QtWidgets.QPushButton(" Δημιουργία backup τώρα")
        btn_bk_now.setIcon(make_icon("export", "#ffffff", 18))
        btn_bk_now.clicked.connect(self._backup_now)
        bl.addRow(btn_bk_now)
        btn_restore = QtWidgets.QPushButton(" Επαναφορά από backup")
        btn_restore.setIcon(make_icon("import", "#ffffff", 18))
        btn_restore.clicked.connect(self._restore)
        bl.addRow(btn_restore)
        layout.addWidget(bk)

        layout.addStretch()

    def refresh(self):
        self.ed_school.setText(self.settings.school_name)
        self.sp_due.setValue(self.settings.due_days)
        self.sp_max.setValue(self.settings.max_loans)
        self.sp_remind.setValue(self.settings.remind_days)
        idx = self.cmb_font.findData(self.settings.font_size)
        if idx >= 0:
            self.cmb_font.setCurrentIndex(idx)
        self.chk_auto.setChecked(self.settings.auto_backup)
        self.ed_bk_password.setText(self.settings.backup_password)
        self.sp_bk_count.setValue(self.settings.backup_count)

    def _save_general(self):
        self.settings.set("school_name", self.ed_school.text().strip() or "Βιβλιοθήκη Σχολείου")
        self.settings.set("due_days", str(self.sp_due.value()))
        self.settings.set("max_loans", str(self.sp_max.value()))
        self.settings.set("remind_days", str(self.sp_remind.value()))
        old_font = self.settings.font_size
        self.settings.set("font_size", self.cmb_font.currentData())
        self.settings.set("auto_backup", "on" if self.chk_auto.isChecked() else "off")
        self.settings.set("backup_password", self.ed_bk_password.text())
        self.settings.set("backup_count", str(self.sp_bk_count.value()))
        if self.cmb_font.currentData() != old_font:
            self.main.apply_font_size()
        QtWidgets.QMessageBox.information(self, "Ρυθμίσεις", "Οι ρυθμίσεις αποθηκεύτηκαν.")
        self.main.status_message("Οι ρυθμίσεις αποθηκεύτηκαν.")

    def _backup_now(self):
        password = self.ed_bk_password.text() or None
        outdir = self.main.backup_dir()
        paths = backup.auto_backup(self.db.path, outdir, keep=self.sp_bk_count.value(), password=password)
        if paths:
            self.main.status_message(f"Backup δημιουργήθηκε: {paths[0]}")
            QtWidgets.QMessageBox.information(self, "Backup", f"Το backup αποθηκεύτηκε:\n{paths[0]}")
        else:
            QtWidgets.QMessageBox.warning(self, "Backup", "Δεν ήταν δυνατή η δημιουργία backup.")

    def _restore(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Επιλογή backup",
                                                        "", "Backup (*.enc *.db);;Όλα (*)")
        if not path:
            return
        ret = QtWidgets.QMessageBox.question(
            self, "Επαναφορά",
            "Προσοχή: τα τρέχοντα δεδομένα θα αντικατασταθούν.\nΘέλετε να συνεχίσετε;")
        if ret != QtWidgets.QMessageBox.Yes:
            return
        tmp = self.main.tmp_path("restore_tmp.db")
        try:
            if path.lower().endswith(".enc"):
                pwd, ok = QtWidgets.QInputDialog.getText(self, "Κωδικός",
                                                         "Δώστε τον κωδικό του backup:",
                                                         QtWidgets.QLineEdit.Password)
                if not ok:
                    return
                backup.decrypt_backup(path, tmp, pwd)
            else:
                import shutil
                shutil.copy2(path, tmp)
            self.db.restore_from(tmp)
            self.main.status_message("Επαναφορά ολοκληρώθηκε.")
            QtWidgets.QMessageBox.information(self, "Επαναφορά", "Η επαναφορά ολοκληρώθηκε.")
            self.main.refresh_pages()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Σφάλμα", str(e))