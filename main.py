import sys
from PySide6 import QtWidgets

from core.paths import db_path
from ui.main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("SchoolLIB")
    app.setOrganizationName("SchoolLIB")
    window = MainWindow(db_path())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()