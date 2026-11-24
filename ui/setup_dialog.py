import os

from PySide6 import QtCore, QtGui, QtWidgets

from core import paths


class SetupDialog(QtWidgets.QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setModal(True)
        self.setMinimumWidth(620)
        self.language = QtWidgets.QComboBox()
        self.language.addItem("English", "en")
        self.language.addItem("Ελληνικά", "el")

        self.ed_school = QtWidgets.QLineEdit()
        self.ed_country = QtWidgets.QLineEdit()
        self.ed_location = QtWidgets.QLineEdit()
        self.ed_phone = QtWidgets.QLineEdit()
        self.ed_email = QtWidgets.QLineEdit()
        self.ed_contact = QtWidgets.QLineEdit()

        self._labels = {}
        self._build()
        self.language.currentIndexChanged.connect(self._retranslate)
        self._retranslate()

    def _build(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(16)

        brand = QtWidgets.QHBoxLayout()
        icon_path = os.path.join(paths.BASE, "icon.png")
        if os.path.exists(icon_path):
            icon = QtWidgets.QLabel()
            icon.setPixmap(QtGui.QPixmap(icon_path).scaled(
                48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            ))
            brand.addWidget(icon)
        heading = QtWidgets.QVBoxLayout()
        self.title_label = QtWidgets.QLabel()
        self.title_label.setObjectName("header")
        self.subtitle_label = QtWidgets.QLabel()
        self.subtitle_label.setObjectName("muted")
        heading.addWidget(self.title_label)
        heading.addWidget(self.subtitle_label)
        brand.addLayout(heading, 1)
        layout.addLayout(brand)

        language_row = QtWidgets.QHBoxLayout()
        self._labels["language"] = QtWidgets.QLabel()
        language_row.addWidget(self._labels["language"])
        language_row.addWidget(self.language, 1)
        layout.addLayout(language_row)

        self.school_group = QtWidgets.QGroupBox()
        form = QtWidgets.QFormLayout(self.school_group)
        form.setSpacing(12)
        fields = (
            ("school", self.ed_school),
            ("country", self.ed_country),
            ("location", self.ed_location),
            ("phone", self.ed_phone),
            ("email", self.ed_email),
            ("contact", self.ed_contact),
        )
        for key, widget in fields:
            label = QtWidgets.QLabel()
            form.addRow(label, widget)
            self._labels[key] = label
        layout.addWidget(self.school_group)

        self.button_box = QtWidgets.QDialogButtonBox()
        self.finish_button = self.button_box.addButton(
            QtWidgets.QDialogButtonBox.Save
        )
        self.cancel_button = self.button_box.addButton(
            QtWidgets.QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def _retranslate(self):
        greek = self.language.currentData() == "el"
        text = {
            "title": "Καλώς ορίσατε στο SchoolLIB" if greek else "Welcome to SchoolLIB",
            "subtitle": "Ας ρυθμίσουμε τη σχολική σας βιβλιοθήκη." if greek
            else "Let's set up your school library.",
            "language": "Γλώσσα εφαρμογής:" if greek else "App language:",
            "group": "Στοιχεία σχολείου" if greek else "School details",
            "school": "Όνομα σχολείου *" if greek else "School name *",
            "country": "Χώρα *" if greek else "Country *",
            "location": "Πόλη / διεύθυνση" if greek else "City / address",
            "phone": "Τηλέφωνο" if greek else "Phone",
            "email": "Email" if greek else "Email",
            "contact": "Υπεύθυνος βιβλιοθήκης" if greek else "Librarian / contact",
            "finish": "Έναρξη" if greek else "Get started",
            "cancel": "Άκυρο" if greek else "Cancel",
            "required": "Συμπληρώστε το όνομα του σχολείου και τη χώρα."
            if greek else "Enter the school name and country to continue.",
        }
        self.setWindowTitle(text["title"])
        self.title_label.setText(text["title"])
        self.subtitle_label.setText(text["subtitle"])
        self.school_group.setTitle(text["group"])
        for key in ("language", "school", "country", "location", "phone", "email", "contact"):
            self._labels[key].setText(text[key])
        self.finish_button.setText(text["finish"])
        self.cancel_button.setText(text["cancel"])
        self._required_message = text["required"]

    def accept(self):
        school = self.ed_school.text().strip()
        country = self.ed_country.text().strip()
        if not school or not country:
            QtWidgets.QMessageBox.warning(self, self.windowTitle(), self._required_message)
            (self.ed_school if not school else self.ed_country).setFocus()
            return

        profile = {
            "school_name": school,
            "school_country": country,
            "school_location": self.ed_location.text().strip(),
            "school_phone": self.ed_phone.text().strip(),
            "school_email": self.ed_email.text().strip(),
            "school_contact": self.ed_contact.text().strip(),
            "language": self.language.currentData(),
            "setup_complete": "true",
        }
        for key, value in profile.items():
            self.settings.set(key, value)
        super().accept()
