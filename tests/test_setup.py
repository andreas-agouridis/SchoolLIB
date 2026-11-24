import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from core.db import LibraryDB
from core.settings import AppSettings
from core import i18n
from ui.setup_dialog import SetupDialog


class SetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "library.db")
        self.settings = AppSettings(LibraryDB(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_setup_requires_school_and_country_then_persists_profile(self):
        self.assertFalse(self.settings.setup_complete)
        dialog = SetupDialog(self.settings)
        self.assertEqual(dialog.language.currentData(), "en")

        with patch.object(QtWidgets.QMessageBox, "warning"):
            dialog.accept()
        self.assertFalse(self.settings.setup_complete)

        dialog.ed_school.setText("North School")
        dialog.ed_country.setText("Greece")
        dialog.ed_location.setText("Athens")
        dialog.ed_phone.setText("+30 210 0000000")
        dialog.ed_email.setText("library@example.org")
        dialog.ed_contact.setText("Librarian")
        dialog.language.setCurrentIndex(1)
        dialog.accept()

        saved = AppSettings(LibraryDB(self.db_path))
        self.assertTrue(saved.setup_complete)
        self.assertEqual(saved.language, "el")
        self.assertEqual(saved.school_name, "North School")
        self.assertEqual(saved.school_country, "Greece")
        self.assertEqual(saved.school_location, "Athens")
        self.assertEqual(saved.school_phone, "+30 210 0000000")
        self.assertEqual(saved.school_email, "library@example.org")
        self.assertEqual(saved.school_contact, "Librarian")

    def test_translation_tracks_selected_language_and_dynamic_counts(self):
        i18n.set_language("en")
        self.assertEqual(i18n.tr("Αρχική"), "Dashboard")
        self.assertEqual(i18n.tr("Διαγράφηκαν 3 βιβλία."), "3 books deleted.")
        self.assertEqual(
            i18n.tr("Class list: 4 εισήχθηκαν, 2 ενημερώθηκαν, 1 παραλείφθηκαν."),
            "Class list: 4 imported, 2 updated, 1 skipped.",
        )
        self.assertEqual(
            i18n.tr("Kαθυστερημένο: The Hobbit -> Alex (λόγω 2026-11-20, υπερημερία 4 ημ.)"),
            "Overdue: The Hobbit -> Alex (due 2026-11-20, 4 days late)",
        )
        i18n.set_language("el")
        self.assertEqual(i18n.tr("Dashboard"), "Αρχική")

    def test_dynamic_loan_lists_keep_user_names(self):
        i18n.set_language("en")
        alerts = QtWidgets.QListWidget()
        alerts.setObjectName("alertsList")
        alerts.addItem(
            "Kαθυστερημένο: The Hobbit -> Alex (λόγω 2026-11-20, υπερημερία 4 ημ.)"
        )
        i18n.translate_widget_tree(alerts)
        self.assertEqual(
            alerts.item(0).text(),
            "Overdue: The Hobbit -> Alex (due 2026-11-20, 4 days late)",
        )

        loans = QtWidgets.QListWidget()
        loans.setObjectName("activeLoanPicker")
        loans.addItem(
            "The Hobbit  [B001] -> Alex  (προθεσμία 2026-11-24, υπόλοιπο 2 ημέρες)"
        )
        i18n.translate_widget_tree(loans)
        self.assertEqual(
            loans.item(0).text(),
            "The Hobbit [B001] -> Alex  (due 2026-11-24, 2 days remaining)",
        )


if __name__ == "__main__":
    unittest.main()
