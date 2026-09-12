from PySide6 import QtCore, QtGui, QtWidgets
from ui.icons import make_icon
from ui import theme


class NavButton(QtWidgets.QPushButton):
    """Sidebar navigation button with dynamic icon color transitions."""

    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self._icon_name = icon_name
        self._base_color = "#8899aa"
        self._hover_color = "#d8e2ec"
        self._active_color = "#ffffff"

        self.setIcon(make_icon(icon_name, self._base_color, 20))
        self.setIconSize(QtCore.QSize(20, 20))
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(48)

        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #8899aa;
                border: none;
                text-align: left;
                padding: 14px 18px 14px 14px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                margin: 2px 8px;
            }
            QPushButton:hover {
                background: #263a50;
                color: #d8e2ec;
            }
            QPushButton:checked {
                background: #2c5f8a;
                color: #ffffff;
                font-weight: 700;
            }
        """)

    def _update_icon(self):
        if self.isChecked():
            color = self._active_color
        elif self.underMouse():
            color = self._hover_color
        else:
            color = self._base_color
        self.setIcon(make_icon(self._icon_name, color, 20))

    def setChecked(self, checked):
        super().setChecked(checked)
        self._update_icon()

    def enterEvent(self, event):
        super().enterEvent(event)
        self._update_icon()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._update_icon()
