class AppSettings:
    def __init__(self, db):
        self.db = db

    def get(self, key, default=""):
        return self.db.get_setting(key, default)

    def set(self, key, value):
        self.db.set_setting(key, value)

    @property
    def due_days(self):
        try:
            return max(1, int(self.get("due_days", "14")))
        except Exception:
            return 14

    @property
    def max_loans(self):
        try:
            return max(1, int(self.get("max_loans", "2")))
        except Exception:
            return 2

    @property
    def remind_days(self):
        try:
            return max(1, int(self.get("remind_days", "3")))
        except Exception:
            return 3

    @property
    def font_size(self):
        return self.get("font_size", "large")

    @property
    def school_name(self):
        return self.get("school_name", "School Library")

    @property
    def school_country(self):
        return self.get("school_country", "")

    @property
    def school_location(self):
        return self.get("school_location", "")

    @property
    def school_phone(self):
        return self.get("school_phone", "")

    @property
    def school_email(self):
        return self.get("school_email", "")

    @property
    def school_contact(self):
        return self.get("school_contact", "")

    @property
    def language(self):
        return self.get("language", "en")

    @property
    def setup_complete(self):
        return self.get("setup_complete", "false") == "true"

    @property
    def auto_backup(self):
        return self.get("auto_backup", "on") == "on"

    @property
    def backup_password(self):
        return self.get("backup_password", "")

    @property
    def backup_count(self):
        try:
            return max(1, int(self.get("backup_count", "5")))
        except Exception:
            return 5

    def to_dict(self):
        return {
            "due_days": self.due_days,
            "max_loans": self.max_loans,
            "remind_days": self.remind_days,
            "font_size": self.font_size,
            "school_name": self.school_name,
            "school_country": self.school_country,
            "school_location": self.school_location,
            "school_phone": self.school_phone,
            "school_email": self.school_email,
            "school_contact": self.school_contact,
            "language": self.language,
            "setup_complete": self.setup_complete,
            "auto_backup": self.auto_backup,
            "backup_password": self.backup_password,
            "backup_count": self.backup_count,
        }