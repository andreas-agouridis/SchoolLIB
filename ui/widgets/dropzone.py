import os

from PySide6 import QtCore, QtWidgets

ALLOWED = (".xlsx", ".xls", ".csv")


class DropZone(QtWidgets.QFrame):
    file_selected = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropzone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        self.title = QtWidgets.QLabel("Σύρετε και αφήστε το αρχείο εδώ")
        self.title.setObjectName("drop_title")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle = QtWidgets.QLabel(
            "ή πατήστε μέσα στη ζώνη για να επιλέξετε αρχείο από τον υπολογιστή\n"
            "(Excel .xlsx, .xls ή .csv)")
        self.subtitle.setObjectName("drop_sub")
        self.subtitle.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle.setWordWrap(True)

        v = QtWidgets.QVBoxLayout(self)
        v.setAlignment(QtCore.Qt.AlignCenter)
        v.setSpacing(10)
        v.addWidget(self.title)
        v.addWidget(self.subtitle)

    def _repaint(self, dragging):
        self.setProperty("drag", dragging)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def dragEnterEvent(self, event):
        if _has_importable_file(event.mimeData()):
            event.acceptProposedAction()
            self._repaint(True)

    def dragLeaveEvent(self, event):
        self._repaint(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        path = _first_importable_file(event.mimeData())
        self._repaint(False)
        if path:
            self.file_selected.emit(path)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Επιλογή αρχείου", "",
            "Αρχεία δεδομένων (*.xlsx *.xls *.csv);;Όλα τα αρχεία (*)")
        if path:
            self.file_selected.emit(path)


def _first_importable_file(mime):
    for url in mime.urls():
        path = url.toLocalFile()
        if path and os.path.splitext(path)[1].lower() in ALLOWED:
            return path
    return None


def _has_importable_file(mime):
    return _first_importable_file(mime) is not None