from PySide6.QtGui import QColor, QFont

PRIMARY = "#2c5f8a"
PRIMARY_DARK = "#1f4464"
ACCENT = "#e67e22"
SUCCESS = "#27ae60"
WARNING = "#f39c12"
DANGER = "#c0392b"
BG = "#f2f5f8"
CARD = "#ffffff"
TEXT = "#22303a"
TEXT_MUTED = "#6b7a86"
SIDEBAR = "#1e2b3a"
SIDEBAR_ACTIVE = "#2c5f8a"


def font_size_cfg(key="large"):
    if key == "xlarge":
        return 16, 22, 32
    return 13, 18, 26


def build_stylesheet(key="large"):
    base, btn, big = font_size_cfg(key)
    return f"""
    * {{
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: {base}px;
        color: {TEXT};
    }}
    QMainWindow, QDialog {{ background: {BG}; }}
    QWidget#page {{ background: {BG}; }}
    QLabel {{ background: transparent; }}
    QLabel#header {{
        font-size: {big}px;
        font-weight: 700;
        color: {PRIMARY_DARK};
        padding: 6px 0 2px 0;
    }}
    QLabel#section {{ font-size: {btn}px; font-weight: 600; color: {PRIMARY_DARK}; }}
    QLabel#muted {{ color: {TEXT_MUTED}; font-size: {str(int(base*0.92))}px; }}
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit, QPlainTextEdit, QDoubleSpinBox {{
        background: {CARD};
        border: 1.5px solid #c5cdd5;
        border-radius: 6px;
        padding: {str(int(base*0.55))}px {str(int(base*0.8))}px;
        min-height: {str(int(base*1.6))}px;
        selection-background-color: {PRIMARY};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
        border: 2px solid {PRIMARY};
    }}
    QPushButton {{
        background: {PRIMARY};
        color: white;
        border: none;
        border-radius: 6px;
        padding: {str(int(base*0.7))}px {str(int(base*1.4))}px;
        font-weight: 600;
        min-height: {str(int(base*1.7))}px;
    }}
    QPushButton:hover {{ background: {PRIMARY_DARK}; }}
    QPushButton:pressed {{ background: #18344f; }}
    QPushButton:disabled {{ background: #b9c3cd; color: #eef2f5; }}
    QPushButton#secondary {{
        background: #e8edf2; color: {PRIMARY_DARK};
    }}
    QPushButton#secondary:hover {{ background: #d5dee7; }}
    QPushButton#danger {{ background: {DANGER}; }}
    QPushButton#danger:hover {{ background: #922b21; }}
    QPushButton#success {{ background: {SUCCESS}; }}
    QPushButton#success:hover {{ background: #1e8449; }}
    QPushButton#warn {{ background: {ACCENT}; }}
    QPushButton#warn:hover {{ background: #c96412; }}
    QPushButton#ghost {{
        background: transparent;
        color: {PRIMARY};
        border: 2px solid {PRIMARY};
    }}
    QPushButton#ghost:hover {{ background: #e8f0f7; }}
    QPushButton#big {{
        font-size: {str(int(btn*0.95))}px;
        padding: {str(int(base*1.1))}px {str(int(base*1.8))}px;
        min-height: {str(int(base*2.4))}px;
        border-radius: 8px;
    }}
    QLineEdit#search {{
        font-size: {str(int(btn*0.85))}px;
        padding: {str(int(base*0.8))}px {str(int(base*1.1))}px;
    }}
    QTableWidget {{
        background: {CARD};
        border: 1px solid #d7dee5;
        border-radius: 6px;
        gridline-color: #e3e8ed;
        alternate-background-color: #f7f9fb;
    }}
    QTableWidget::item {{ padding: 6px; }}
    QTableWidget::item:selected {{ background: #dbe7f3; color: {TEXT}; }}
    QHeaderView::section {{
        background: {PRIMARY_DARK};
        color: white;
        border: none;
        padding: 8px 10px;
        font-weight: 600;
        font-size: {str(int(base*0.95))}px;
    }}
    QListWidget, QTreeWidget {{
        background: {CARD};
        border: 1px solid #d7dee5;
        border-radius: 6px;
    }}
    QListWidget::item, QTreeWidget::item {{ padding: {str(int(base*0.4))}px; }}
    QListWidget::item:selected, QTreeWidget::item:selected {{ background: #dbe7f3; }}
    QGroupBox {{
        background: {CARD};
        border: 1px solid #d7dee5;
        border-radius: 8px;
        margin-top: {str(int(base*1.2))}px;
        padding-top: {str(int(base*0.9))}px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: {str(int(base*0.7))}px;
        padding: 0 {str(int(base*0.4))}px;
        color: {PRIMARY_DARK};
    }}
    QTabWidget::pane {{ border: 1px solid #d7dee5; border-radius: 6px; background: {CARD}; }}
    QTabBar::tab {{
        background: #e3e9ef;
        padding: {str(int(base*0.8))}px {str(int(base*1.5))}px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 3px;
        font-weight: 600;
    }}
    QTabBar::tab:selected {{ background: {PRIMARY}; color: white; }}
    QScrollBar:vertical {{ background: transparent; width: 12px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: #b9c3cd; border-radius: 5px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {PRIMARY}; }}
    QScrollBar:horizontal {{ background: transparent; height: 12px; margin: 2px; }}
    QScrollBar::handle:horizontal {{ background: #b9c3cd; border-radius: 5px; min-width: 30px; }}
    QScrollBar::handle:horizontal:hover {{ background: {PRIMARY}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QFrame#dropzone {{
        background: #f6f9fc;
        border: 2px dashed #a9bccb;
        border-radius: 14px;
    }}
    QFrame#dropzone:hover {{ background: #eef4f9; }}
    QFrame#dropzone[drag="true"] {{
        background: #e5f1fa;
        border: 2px dashed {PRIMARY};
    }}
    QLabel#drop_title {{ font-size: {str(int(btn*0.95))}px; font-weight: 700; color: {PRIMARY_DARK}; }}
    QLabel#drop_sub {{ font-size: {str(int(base*0.92))}px; color: {TEXT_MUTED}; }}
    QStatusBar {{ background: {PRIMARY_DARK}; color: white; font-size: {str(int(base*0.95))}px; }}
    QStatusBar QLabel {{ color: white; background: transparent; }}
    QMessageBox QLabel {{ font-size: {base}px; }}
    QCalendarWidget QWidget {{ background: {CARD}; }}
    QCalendarWidget QAbstractItemView:enabled {{
        color: {TEXT};
        selection-background-color: {PRIMARY};
        selection-color: white;
    }}
    QToolTip {{
        background: {PRIMARY_DARK};
        color: white;
        border: none;
        padding: 6px;
        font-size: {str(int(base*0.92))}px;
    }}
    """


def card_style():
    return f"""
    QFrame#card {{
        background: {CARD};
        border: 1px solid #dbe2ea;
        border-radius: 10px;
    }}
    QLabel#card_value {{ font-size: 30px; font-weight: 800; color: {PRIMARY_DARK}; }}
    QLabel#card_title {{ font-size: 14px; font-weight: 600; color: {TEXT_MUTED}; }}
    """


def header_font(scale=1.0):
    f = QFont("Segoe UI", 18 * scale)
    f.setBold(True)
    return f