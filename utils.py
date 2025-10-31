import qrcode, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import hashlib as _hashlib

def generate_qr_png(data, outpath):
    img = qrcode.make(data)
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    img.save(outpath)
    return outpath

def export_books_pdf_labels(books, outfile="labels.pdf"):
    c = canvas.Canvas(outfile, pagesize=A4)
    width, height = A4
    x, y = 40, height-80
    for b in books:
        text = f"{b.get('title','')}\\n{b.get('author','')}\\nID: {b.get('book_number','')}"
        c.rect(x-5, y-35, 250, 70, stroke=1, fill=0)
        c.drawString(x, y, b.get('title',''))
        c.drawString(x, y-15, b.get('author',''))
        c.drawString(x, y-30, f"ID: {b.get('book_number','')}" )
        y -= 90
        if y < 80:
            c.showPage(); y = height-80
    c.save()
    return outfile

def encrypt_backup(db_path, outpath, password):
    salt = get_random_bytes(16)
    key = _hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200000, dklen=32)
    cipher = AES.new(key, AES.MODE_GCM)
    with open(db_path, "rb") as f:
        data = f.read()
    ciphertext, tag = cipher.encrypt_and_digest(data)
    with open(outpath, "wb") as out:
        out.write(salt); out.write(cipher.nonce); out.write(tag); out.write(ciphertext)
    return outpath
