import datetime

from PySide6 import QtCore, QtGui, QtWidgets

from services import exporter
from ui.icons import make_icon
from ui.widgets.calendar_widget import DueCalendar
from ui import theme


class CalendarPage(QtWidgets.QWidget):
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
        header = QtWidgets.QLabel("Ημερολόγιο Προθεσμιών")
        header.setObjectName("header")
        layout.addWidget(header)

        main_w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(main_w)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(16)
        self.calendar = DueCalendar()
        self.calendar.setMinimumWidth(520)
        h.addWidget(self.calendar, 2)
        right = QtWidgets.QWidget()
        rv = QtWidgets.QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        lbl = QtWidgets.QLabel("Δάνεια της ημέρας")
        lbl.setObjectName("section")
        rv.addWidget(lbl)
        self.loans_list = QtWidgets.QListWidget()
        rv.addWidget(self.loans_list, 1)
        btn_export = QtWidgets.QPushButton(" Εξαγωγή")
        btn_export.setIcon(make_icon("export", "#ffffff", 18))
        btn_export.clicked.connect(self._export_day)
        rv.addWidget(btn_export)
        h.addWidget(right, 1)
        layout.addWidget(main_w, 1)
        layout.addWidget(QtWidgets.QLabel("Οι κουκκίδες δείχνουν πόσες επιστροφές λήγουν κάθε μέρα. "
                                          "Κόκκινη σημαίνει ότι κάποια έχουν ήδη λήξει.",
                                          objectName="muted"))

        self.calendar.date_selected.connect(self._show_day)

    def refresh(self):
        self._reload_marks()
        self._show_day(self.calendar.selectedDate().toPython())

    def _reload_marks(self):
        marks = {}
        loans = self.db.active_loans()
        today = datetime.date.today()
        for l in loans:
            try:
                d = datetime.date.fromisoformat(l["due_date"][:10])
            except ValueError:
                continue
            if d not in marks:
                marks[d] = [0, False]
            marks[d][0] += 1
            if d < today:
                marks[d][1] = True
        self.calendar.set_marks(marks)
        self._loans = loans

    def _show_day(self, date):
        self.loans_list.clear()
        selected = date
        for l in self._loans or []:
            try:
                d = datetime.date.fromisoformat(l["due_date"][:10])
            except ValueError:
                continue
            if d == selected:
                overdue = l["days_left"] < 0
                text = (f"{l['book_title']} -> {l['member_name']}  "
                        f"(προθεσμία {l['due_date']})")
                item = QtWidgets.QListWidgetItem(text)
                item.setData(QtCore.Qt.UserRole, l)
                if overdue:
                    item.setForeground(QtGui.QBrush(theme.DANGER))
                self.loans_list.addItem(item)
        if self.loans_list.count() == 0:
            self.loans_list.addItem(QtWidgets.QListWidgetItem("Δεν υπάρχουν δάνεια για αυτήν την ημέρα."))

    def _export_day(self):
        selected = self.calendar.selectedDate().toPython()
        rows = [l for l in (self._loans or [])
                if l["due_date"][:10] == selected.isoformat()]
        if not rows:
            QtWidgets.QMessageBox.information(self, "Εξαγωγή", "Δεν υπάρχουν δάνεια για αυτή την ημέρα.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Εξαγωγή ημέρας", f"daneia_{selected}.xlsx",
                                                        "Excel (*.xlsx);;CSV (*.csv);;PDF (*.pdf)")
        if not path:
            return
        fmt = exporter.autodetect_format(path)
        data = []
        for l in rows:
            d = dict(l)
            d["member"] = d.pop("member_name", "")
            d["book"] = d.pop("book_title", "")
            d["status"] = "Υπερημερία" if l["days_left"] < 0 else "Κανονικό"
            data.append(d)
        exporter.export_rows(data, ["book", "member", "due_date", "status"], path, fmt=fmt,
                             title=f"Δάνεια {selected}", school_name=self.main.settings.school_name)
        self.main.status_message("Η εξαγωγή ολοκληρώθηκε.")