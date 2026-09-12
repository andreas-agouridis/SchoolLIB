from PySide6 import QtCore, QtGui, QtWidgets

from ui import theme
from ui.icons import make_icon


class ActionCard(QtWidgets.QFrame):
    clicked = QtCore.Signal()

    def __init__(self, title, subtitle, parent=None, icon_name=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(theme.card_style())
        self.setCursor(QtCore.Qt.PointingHandCursor)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        if icon_name:
            row = QtWidgets.QHBoxLayout()
            ic = QtWidgets.QLabel()
            ic.setPixmap(make_icon(icon_name, theme.PRIMARY, 28).pixmap(28, 28))
            row.addWidget(ic)
            self.title_lbl = QtWidgets.QLabel(title)
            self.title_lbl.setObjectName("section")
            row.addWidget(self.title_lbl)
            row.addStretch()
            layout.addLayout(row)
        else:
            self.title_lbl = QtWidgets.QLabel(title)
            self.title_lbl.setObjectName("section")
            layout.addWidget(self.title_lbl)
        self.sub_lbl = QtWidgets.QLabel(subtitle)
        self.sub_lbl.setObjectName("muted")
        self.sub_lbl.setWordWrap(True)
        layout.addWidget(self.sub_lbl)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class StatCard(QtWidgets.QFrame):
    def __init__(self, title, value="0", note="", accent=theme.PRIMARY, parent=None, icon_name=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(theme.card_style())
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        top_row = QtWidgets.QHBoxLayout()
        top_row.setSpacing(10)
        if icon_name:
            ic = QtWidgets.QLabel()
            ic.setPixmap(make_icon(icon_name, accent, 26).pixmap(26, 26))
            top_row.addWidget(ic)
        self.value_lbl = QtWidgets.QLabel(str(value))
        self.value_lbl.setObjectName("card_value")
        self.value_lbl.setStyleSheet(f"QLabel#card_value {{ color: {accent}; }}")
        top_row.addWidget(self.value_lbl)
        top_row.addStretch()
        layout.addLayout(top_row)
        self.title_lbl = QtWidgets.QLabel(title)
        self.title_lbl.setObjectName("card_title")
        layout.addWidget(self.title_lbl)
        if note:
            note_lbl = QtWidgets.QLabel(note)
            note_lbl.setObjectName("muted")
            note_lbl.setStyleSheet("font-size: 12px;")
            layout.addWidget(note_lbl)


class BigButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None, kind=None, big=False):
        super().__init__(text, parent)
        if big:
            self.setObjectName("big")
        if kind:
            self.setObjectName(kind)