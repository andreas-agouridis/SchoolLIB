from PySide6 import QtCore, QtGui, QtWidgets

from ui import theme
from ui.widgets.big_buttons import StatCard, ActionCard


class DashboardPage(QtWidgets.QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.setObjectName("page")
        self._build()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        header = QtWidgets.QLabel("Αρχική")
        header.setObjectName("header")
        layout.addWidget(header)

        self.stats_grid = QtWidgets.QGridLayout()
        self.stats_grid.setSpacing(12)
        layout.addLayout(self.stats_grid)

        self.quick_row = QtWidgets.QHBoxLayout()
        self.quick_row.setSpacing(12)
        layout.addLayout(self.quick_row)

        charts_widget = QtWidgets.QWidget()
        charts_layout = QtWidgets.QHBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(12)
        self.top_box = QtWidgets.QFrame()
        self.top_box.setObjectName("card")
        self.top_box.setStyleSheet(theme.card_style())
        tb_l = QtWidgets.QVBoxLayout(self.top_box)
        tb_l.addWidget(self._section("Δημοφιλέστερα βιβλία"))
        self.top_chart_wrap = QtWidgets.QWidget()
        self.top_chart_layout = QtWidgets.QVBoxLayout(self.top_chart_wrap)
        self.top_chart_layout.setContentsMargins(0, 0, 0, 0)
        tb_l.addWidget(self.top_chart_wrap, 1)
        charts_layout.addWidget(self.top_box, 3)

        self.cat_box = QtWidgets.QFrame()
        self.cat_box.setObjectName("card")
        self.cat_box.setStyleSheet(theme.card_style())
        cb_l = QtWidgets.QVBoxLayout(self.cat_box)
        cb_l.addWidget(self._section("Κατανομή κατηγοριών"))
        self.cat_chart_wrap = QtWidgets.QWidget()
        self.cat_chart_layout = QtWidgets.QVBoxLayout(self.cat_chart_wrap)
        self.cat_chart_layout.setContentsMargins(0, 0, 0, 0)
        cb_l.addWidget(self.cat_chart_wrap, 1)
        charts_layout.addWidget(self.cat_box, 2)

        layout.addWidget(charts_widget, 1)

        self.alerts = QtWidgets.QFrame()
        self.alerts.setObjectName("card")
        self.alerts.setStyleSheet(theme.card_style())
        a_l = QtWidgets.QVBoxLayout(self.alerts)
        a_l.addWidget(self._section("Προσοχή"))
        self.alerts_list = QtWidgets.QListWidget()
        self.alerts_list.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.alerts_list.setFrameShape(QtWidgets.QFrame.NoFrame)
        a_l.addWidget(self.alerts_list, 1)
        layout.addWidget(self.alerts, 1)

    def _section(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setObjectName("section")
        return lbl

    def refresh(self):
        s = self.db.stats()

        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cards = [
            ("Βιβλία στους καταλόγους", s["books"], f"Συνολικά {s['copies']} αντίτυπα", theme.PRIMARY, "book"),
            ("Μέλη", s["members"], f"Σε {s['libraries']} βιβλιοθήκες", theme.SUCCESS, "users"),
            ("Ενεργά δάνεια", s["active_loans"], f"Συνολικά {s['loans_total']} δανεισμοί", theme.ACCENT, "loan"),
            ("Καθυστερημένες επιστροφές", s["overdue"], f"{s['due_soon']} λήγουν σύντομα", theme.DANGER, "warning"),
        ]
        for i, (title, val, note, color, icon) in enumerate(cards):
            card = StatCard(title, val, note, color, icon_name=icon)
            self.stats_grid.addWidget(card, i // 4, i % 4)

        for i in range(self.stats_grid.columnCount()):
            self.stats_grid.setColumnStretch(i, 1)

        while self.quick_row.count():
            item = self.quick_row.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        actions = [
            ("Δανεισμός βιβλίου", "Καταχώρηση νέου δανείου", self.main.open_loan_dialog, "loan"),
            ("Προσθήκη βιβλίου", "Νέο βιβλίο στον κατάλογο", self.main.open_add_book, "add"),
            ("Προσθήκη μέλους", "Εγγραφή νέου μέλους", self.main.open_add_member, "users"),
            ("Υπενθυμίσεις", "Ληγμένα και επικείμενα δάνεια", self.main.show_reminders, "warning"),
        ]
        for title, sub, cb, icon in actions:
            card = ActionCard(title, sub, icon_name=icon)
            card.clicked.connect(cb)
            self.quick_row.addWidget(card)

        self._refresh_charts(s)
        self._refresh_alerts(s)

    def _refresh_charts(self, s):
        from PySide6.QtCharts import (QChart, QChartView, QBarSeries, QBarSet,
                                      QBarCategoryAxis, QValueAxis, QPieSeries)
        from PySide6.QtGui import QBrush, QColor, QFont, QPen
        from ui import theme
        while self.top_chart_layout.count():
            item = self.top_chart_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        while self.cat_chart_layout.count():
            item = self.cat_chart_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        COLORS = [
            QColor("#2c5f8a"), QColor("#27ae60"), QColor("#e67e22"),
            QColor("#c0392b"), QColor("#8e44ad"), QColor("#2980b9"),
            QColor("#16a085"), QColor("#d35400"),
        ]

        top = self.db.top_books(8)

        series = QBarSeries()
        bset = QBarSet("Δανεισμοί")
        bset.setColor(QColor("#2c5f8a"))
        bset.setBorderColor(QColor("#1f4464"))
        labels = []
        for t in top:
            bset.append(float(t["times"]))
            labels.append((t["title"] or "?")[:20])
        series.append(bset)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(False)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        bg_brush = QBrush(QColor("#ffffff"))
        chart.setBackgroundBrush(bg_brush)
        chart.setDropShadowEnabled(False)
        font = QFont("Segoe UI", 9)
        axis_x = QBarCategoryAxis()
        axis_x.append(labels)
        axis_x.setLabelsFont(font)
        axis_x.setLabelsColor(QColor("#22303a"))
        axis_x.setLinePenColor(QColor("#d5dde5"))
        chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setLabelsFont(font)
        axis_y.setLabelsColor(QColor("#6b7a86"))
        axis_y.setGridLineColor(QColor("#e3e8ed"))
        axis_y.setLinePenColor(QColor("#d5dde5"))
        chart.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)
        chart.setPlotAreaBackgroundVisible(False)
        view = QChartView(chart)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setMinimumHeight(220)
        self.top_chart_layout.addWidget(view)

        cats = self.db.categories_distribution()
        pie = QPieSeries()
        pie.setHoleSize(0.42)
        if not cats:
            pie.append("Χωρίς κατηγορίες", 1)
        for i, c in enumerate(cats):
            sl = pie.append(c["name"] or "?", float(c["cnt"]))
            sl.setBrush(QBrush(COLORS[i % len(COLORS)]))
        for sl in pie.slices():
            if len(pie.slices()) <= 8:
                sl.setLabelVisible(True)
                sl.setLabel(sl.label()[:15])
                sl.setLabelFont(font)
                sl.setLabelColor(QColor("#22303a"))
        chart2 = QChart()
        chart2.addSeries(pie)
        chart2.legend().setVisible(False)
        chart2.setAnimationOptions(QChart.SeriesAnimations)
        chart2.setBackgroundBrush(bg_brush)
        chart2.setDropShadowEnabled(False)
        chart2.setPlotAreaBackgroundVisible(False)
        view2 = QChartView(chart2)
        view2.setRenderHint(QtGui.QPainter.Antialiasing)
        view2.setMinimumHeight(220)
        self.cat_chart_layout.addWidget(view2)

    def _refresh_alerts(self, s):
        self.alerts_list.clear()
        remind = int(self.db.get_setting("remind_days", "3") or 3)
        overdue = self.db.overdue_loans()
        upcoming = self.db.upcoming_loans(remind)
        if not overdue and not upcoming:
            empty = QtWidgets.QListWidgetItem("Δεν υπάρχουν εκκρεμότητες. Όλα είναι εντάξει.")
            empty.setForeground(QtGui.QBrush(theme.SUCCESS))
            self.alerts_list.addItem(empty)
            return
        for l in overdue:
            item = QtWidgets.QListWidgetItem(
                f"Kαθυστερημένο: {l['book_title']} -> {l['member_name']} (λόγω {l['due_date']}, "
                f"υπερημερία {abs(l['days_left'])} ημ.)")
            item.setForeground(QtGui.QBrush(theme.DANGER))
            self.alerts_list.addItem(item)
        for l in upcoming:
            item = QtWidgets.QListWidgetItem(
                f"Λήγει σύντομα: {l['book_title']} -> {l['member_name']} (σ {l['due_date']})")
            item.setForeground(QtGui.QBrush(theme.ACCENT))
            self.alerts_list.addItem(item)

    def keyPressEvent(self, event):
        self.main.keyPressEvent(event)