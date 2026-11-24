from PySide6 import QtCore, QtGui, QtWidgets
from ui.icons import make_icon
from ui import theme


class NavButton(QtWidgets.QPushButton):
    """Sidebar navigation button with dynamic icon color transitions."""

    def __init__(self, text, icon_name, parent=None):
        super().__init__(text, parent)
        self._icon_name = icon_name
        self._base_color = "#aebcd0"
        self._hover_color = "#ffffff"
        self._active_color = "#ffffff"

        self.setIcon(make_icon(icon_name, self._base_color, 20))
        self.setIconSize(QtCore.QSize(20, 20))
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setFixedHeight(48)

        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: #aebcd0;
                border: none;
                text-align: left;
                padding: 12px 18px 12px 14px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 9px;
                margin: 2px 10px;
            }}
            QPushButton:hover {{
                background: #25364a;
                color: #ffffff;
            }}
            QPushButton:checked {{
                background: {theme.SIDEBAR_ACTIVE};
                color: #ffffff;
                font-weight: 700;
            }}
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
