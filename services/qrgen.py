import os
import qrcode

QR_DIR = "qr_tmp"


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def book_qr_data(book):
    return f"SCHOOLLIB-BOOK:{book.get('book_number','')}"


def member_qr_data(member):
    return f"SCHOOLLIB-MEMBER:{member.get('member_number','')}"


def qr_png(data, outpath, box_size=8, border=2):
    ensure_dir(os.path.dirname(outpath))
    img = qrcode.make(data, box_size=box_size, border=border)
    img.save(outpath)
    return outpath


def book_qr_png(book, outdir=QR_DIR, box_size=6):
    ensure_dir(outdir)
    path = os.path.join(outdir, f"book_{book.get('book_number','x')}.png")
    return qr_png(book_qr_data(book), path, box_size=box_size)


def member_qr_png(member, outdir=QR_DIR, box_size=6):
    ensure_dir(outdir)
    path = os.path.join(outdir, f"member_{member.get('member_number','x')}.png")
    return qr_png(member_qr_data(member), path, box_size=box_size)