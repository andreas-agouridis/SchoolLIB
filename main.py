import sys
from PySide6 import QtWidgets, QtCore

from core.paths import db_path
from core.db import LibraryDB
from core.settings import AppSettings
from core import i18n
from ui import theme
from ui.main_window import MainWindow
from ui.setup_dialog import SetupDialog

APP_VERSION = "2.0.0"
APP_NAME = "SchoolLIB"
APP_COPYRIGHT = "Copyright (c) Andreas Agouridis"
APP_URL = "https://apps.andreasagouridis.com/schoollib"


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Andreas Agouridis")
    app.setOrganizationDomain("andreasagouridis.com")
    app.setApplicationVersion(APP_VERSION)
    QtCore.QCoreApplication.setApplicationName(APP_NAME)
    QtCore.QCoreApplication.setOrganizationName("Andreas Agouridis")
    QtCore.QCoreApplication.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(theme.build_stylesheet())

    db = LibraryDB(db_path())
    settings = AppSettings(db)
    if not settings.setup_complete:
        setup = SetupDialog(settings)
        if setup.exec() != QtWidgets.QDialog.Accepted:
            return

    i18n.set_language(settings.language)
    i18n.install(app)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
