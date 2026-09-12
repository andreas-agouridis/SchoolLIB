from PySide6 import QtCore, QtGui, QtWidgets

from ui import theme


class DueCalendar(QtWidgets.QCalendarWidget):
    date_selected = QtCore.Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._marks = {}  # date -> (count, overdue:bool)
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QtWidgets.QCalendarWidget.SingleLetterDayNames)
        self.clicked.connect(lambda d: self.date_selected.emit(d.toPython()))

    def set_marks(self, marks):
        self._marks = marks
        self.updateCells()

    def paintCell(self, painter, rect, date):
        painter.save()
        super().paintCell(painter, rect, date)
        d = date.toPython()
        mark = self._marks.get(d)
        if mark and mark[0] > 0:
            overdue = mark[1]
            color = theme.DANGER if overdue else theme.ACCENT
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QColor(color))
            x = rect.center().x()
            y = rect.top() + 6
            r = 4 if mark[0] < 10 else 6
            painter.drawEllipse(QtCore.QPoint(x, y), r, r)
        painter.restore()