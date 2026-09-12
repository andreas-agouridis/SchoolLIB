import os
import tempfile
from collections import OrderedDict
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from services import qrgen

_FONT_NAME = "Helvetica"
_FONT_BOLD = "Helvetica-Bold"
_FONT_INITED = False


def _init_font():
    global _FONT_NAME, _FONT_BOLD, _FONT_INITED
    if _FONT_INITED:
        return
    candidates = [
        (r"C:\Windows\Fonts\arial.ttf", "Arial"),
        (r"C:\Windows\Fonts\segoeui.ttf", "SegoeUI"),
        (r"C:\Windows\Fonts\tahoma.ttf", "Tahoma"),
        (r"DejaVuSans.ttf", "DejaVuSans"),
    ]
    for path, name in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                _FONT_NAME = name
                _FONT_BOLD = name
                _FONT_INITED = True
                return
            except Exception:
                continue
    _FONT_INITED = True


def _txt(c, text, x, y, size, bold=False, color=colors.black, align="left"):
    _init_font()
    font = _FONT_BOLD if bold else _FONT_NAME
    c.setFont(font, size)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, (text or ""))
    elif align == "right":
        c.drawRightString(x, y, (text or ""))
    else:
        c.drawString(x, y, (text or ""))


def _fit(c, text, x, y, max_width, size, bold=False, color=colors.black):
    _init_font()
    line = (text or "")
    if c.stringWidth(line, _FONT_BOLD if bold else _FONT_NAME, size) > max_width:
        while c.stringWidth(line + "...", _FONT_BOLD if bold else _FONT_NAME, size) > max_width and len(line) > 1:
            line = line[:-1]
        line += "..."
    _txt(c, line, x, y, size, bold, color)


def _temp_png():
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    return path


def _draw_qr(c, data, x, y, size, tmp_path):
    qrgen.qr_png(data, tmp_path, box_size=6)
    try:
        c.drawImage(tmp_path, x, y, width=size, height=size, mask="auto")
    except Exception:
        pass


def book_labels_pdf(books, outfile, school_name="Βιβλιοθήκη Σχολείου"):
    _init_font()
    c = canvas.Canvas(outfile, pagesize=A4)
    width, height = A4
    cols, rows = 3, 7
    margin = 12 * mm
    label_w = (width - 2 * margin - 2 * 4 * mm) / cols
    label_h = (height - 2 * margin - 6 * 2 * mm) / rows
    tmp = _temp_png()
    for idx, b in enumerate(books):
        pos = idx % (cols * rows)
        if pos == 0 and idx > 0:
            c.showPage()
        col = pos % cols
        row = pos // cols
        x = margin + col * (label_w + 4 * mm)
        y = height - margin - (row + 1) * label_h
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.rect(x, y, label_w, label_h)
        qr_size = label_h * 0.72
        qr_x = x + 2 * mm
        qr_y = y + (label_h - qr_size) / 2
        _draw_qr(c, qrgen.book_qr_data(b), qr_x, qr_y, qr_size, tmp)
        tx = qr_x + qr_size + 3 * mm
        tw = label_w - qr_size - 6 * mm
        _fit(c, b.get("title", ""), tx, y + label_h - 8 * mm, tw, 9, bold=True)
        _fit(c, b.get("author", ""), tx, y + label_h - 17 * mm, tw, 8)
        _fit(c, ("Αρ. " + (b.get("book_number", "") or "")), tx, y + label_h - 25 * mm, tw, 7)
        if b.get("isbn"):
            _fit(c, ("ISBN " + b.get("isbn", "")), tx, y + label_h - 32 * mm, tw, 7)
    c.showPage()
    c.save()
    try:
        os.remove(tmp)
    except OSError:
        pass
    return outfile


def member_cards_pdf(members, outfile, school_name="Βιβλιοθήκη Σχολείου"):
    import datetime
    _init_font()
    c = canvas.Canvas(outfile, pagesize=A4)
    width, height = A4
    cols, rows = 2, 4
    margin = 12 * mm
    gap = 5 * mm
    card_w = (width - 2 * margin - (cols - 1) * gap) / cols
    card_h = (height - 2 * margin - (rows - 1) * 6 * mm) / rows
    tmp = _temp_png()
    blue = colors.HexColor("#2c5f8a")
    lig = colors.HexColor("#eef3f8")
    grn = colors.HexColor("#27ae60")
    grey = colors.HexColor("#7a8794")
    today = datetime.date.today()
    issued = f"{today.day:02d}/{today.month:02d}/{today.year}"
    for idx, m in enumerate(members):
        pos = idx % (cols * rows)
        if pos == 0 and idx > 0:
            c.showPage()
        col = pos % cols
        row = pos // cols
        x = margin + col * (card_w + gap)
        y = height - margin - (row + 1) * card_h
        pad = 2.5 * mm

        c.setStrokeColor(colors.HexColor("#d5dde5"))
        c.setLineWidth(0.8)
        c.roundRect(x, y, card_w, card_h, 5, stroke=1, fill=0)
        c.setFillColor(lig)
        c.roundRect(x + 1, y + 1, card_w - 2, card_h - 2, 4, stroke=0, fill=1)

        hh = 17 * mm
        c.setFillColor(blue)
        c.roundRect(x + pad, y + card_h - hh, card_w - 2 * pad, hh, 4, stroke=0, fill=1)
        _txt(c, (school_name or ""), x + card_w / 2, y + card_h - 11 * mm, 11, bold=True, color=colors.white, align="center")
        _txt(c, "ΔΕΛΤΙΟ ΜΕΛΟΥΣ", x + card_w / 2, y + card_h - 15.5 * mm, 7, bold=True, color=colors.HexColor("#c9d8e8"), align="center")

        qr = card_h - 42 * mm
        qx = x + card_w - qr - 6 * mm
        qy = y + 13 * mm
        c.setFillColor(colors.white)
        c.roundRect(qx - 2 * mm, qy - 2 * mm, qr + 4 * mm, qr + 4 * mm, 3, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor("#c2cdd7"))
        c.setLineWidth(0.5)
        c.roundRect(qx - 2 * mm, qy - 2 * mm, qr + 4 * mm, qr + 4 * mm, 3, stroke=1, fill=0)
        _draw_qr(c, qrgen.member_qr_data(m), qx, qy, qr, tmp)
        _txt(c, "Σκανάρετε", qx + qr / 2, qy - 3 * mm, 6, color=grey, align="center")

        tx = x + 7 * mm
        tw = card_w - qr - 16 * mm
        _fit(c, (m.get("name", "") or ""), tx, y + card_h - 26 * mm, tw, 12, bold=True, color=colors.HexColor("#22303a"))
        c.setStrokeColor(colors.HexColor("#d5dde5"))
        c.setLineWidth(0.5)
        c.line(tx, y + card_h - 29 * mm, tx + tw, y + card_h - 29 * mm)

        local = {
            "Αρ. Μέλους": (m.get("member_number", "") or ""),
            "Τάξη": (m.get("class", "") or ""),
            "Ημ. Έκδοσης": issued,
        }
        ly = y + card_h - 38 * mm
        for label, value in local.items():
            if not value:
                continue
            _txt(c, label, tx, ly, 7, color=grey)
            _txt(c, value, tx + 26 * mm, ly, 9.5, bold=True, color=colors.HexColor("#1f4464"))
            ly -= 9.5 * mm

        c.setFillColor(grn)
        c.roundRect(x + pad, y + 2.5 * mm, card_w - 2 * pad, 5 * mm, 2, stroke=0, fill=1)
        _txt(c, "ΜΕΛΟΣ ΤΗΣ ΒΙΒΛΙΟΘΗΚΗΣ", x + card_w / 2, y + 3.5 * mm, 6.5, bold=True, color=colors.white, align="center")
    c.showPage()
    c.save()
    try:
        os.remove(tmp)
    except OSError:
        pass
    return outfile


def _group_by_member(loans):
    groups = OrderedDict()
    for l in loans:
        groups.setdefault((l["member_id"], l["member_name"]), []).append(l)
    return groups


def reminders_pdf(loans, outfile, school_name="Βιβλιοθήκη Σχολείου", title="Υπενθύμιση Επιστροφής Βιβλίων"):
    _init_font()
    c = canvas.Canvas(outfile, pagesize=A4)
    width, height = A4
    groups = _group_by_member(loans)
    for (mem_id, mem_name), items in groups.items():
        c.setStrokeColor(colors.black)
        c.setLineWidth(1.2)
        c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)
        _txt(c, (school_name or ""), width / 2, height - 34 * mm, 14, bold=True, align="center")
        _txt(c, title, width / 2, height - 44 * mm, 11, align="center")
        _txt(c, ("Αγαπητή/έ " + (mem_name or "")), 25 * mm, height - 66 * mm, 12)
        _txt(c, "Παρακαλούμε να επιστρέψετε τα παρακάτω βιβλία στη βιβλιοθήκη:", 25 * mm, height - 80 * mm, 11)
        y = height - 96 * mm
        for it in items:
            if y < 50 * mm:
                c.showPage()
                y = height - 40 * mm
            _fit(c, ("- " + it.get("book_title", "")), 25 * mm, y, width - 50 * mm, 11)
            _txt(c, ("Προθεσμία: " + (it.get("due_date", "") or "")), width - 35 * mm, y, 10, align="right")
            y -= 11 * mm
        _txt(c, "Ευχαριστούμε για τη συνεργασία.", 25 * mm, y - 10 * mm, 11)
        c.showPage()
    c.save()
    return outfile


def table_pdf(rows, headers, outfile, title="Λίστα", school_name="Βιβλιοθήκη Σχολείου"):
    _init_font()
    c = canvas.Canvas(outfile, pagesize=A4)
    width, height = A4
    col_w = width - 30 * mm
    _txt(c, (school_name or ""), 15 * mm, height - 20 * mm, 13, bold=True)
    _txt(c, title, 15 * mm, height - 30 * mm, 11)
    y = height - 45 * mm
    cell_h = 7 * mm
    for row in rows:
        if y < 18 * mm:
            c.showPage()
            y = height - 20 * mm
        y -= cell_h
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.4)
        c.rect(15 * mm, y, col_w, cell_h, stroke=1, fill=0)
        for i, cell in enumerate(row):
            x = 17 * mm + i * ((col_w - 4 * mm) / len(headers))
            _fit(c, str(cell), x, y + 2 * mm, (col_w - 4 * mm) / len(headers), 8)
    c.save()
    return outfile