import os
import sys


def base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE = base_dir()


def db_path():
    return os.path.join(BASE, "library.db")


def data_dir(*parts):
    d = os.path.join(BASE, "data")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, *parts)


def backups_dir(name=None):
    d = os.path.join(BASE, "backups")
    os.makedirs(d, exist_ok=True)
    return d if name is None else os.path.join(d, name)


def qr_dir():
    d = os.path.join(BASE, "qr_tmp")
    os.makedirs(d, exist_ok=True)
    return d