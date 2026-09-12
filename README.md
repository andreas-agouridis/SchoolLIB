# SchoolLIB

Τοπική εφαρμογή διαχείρισης σχολικής βιβλιοθήκης

Το SchoolLIB είναι μια εφαρμογή γραφείου (desktop app) που δημιουργήθηκε με Python και PySide6, σχεδιασμένη για να βοηθά τα σχολεία να οργανώνουν και να διαχειρίζονται εύκολα τη σχολική τους βιβλιοθήκη χωρίς σύνδεση στο διαδίκτυο.

https://schoollib.world

---

## Εικόνες

<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/d291ae81-01ef-44cb-be01-4b9fe5773d32" />
<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/434281f5-5ee9-4037-b4a1-96846b58206a" />
<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/a2850e85-dc17-4c8c-b0d0-2c8b66c99acd" />
<img width="1919" height="1035" alt="image" src="https://github.com/user-attachments/assets/2b92e11e-3638-43cb-9984-780888ebb5ad" />
<img width="1919" height="1026" alt="image" src="https://github.com/user-attachments/assets/3a7c700e-09cf-4019-bfa9-ed457c623f66" />
<img width="1919" height="1025" alt="image" src="https://github.com/user-attachments/assets/d3ba8987-992d-4563-b018-d670a8b5b902" />
<img width="1919" height="1031" alt="image" src="https://github.com/user-attachments/assets/b2319474-c411-4c4a-bc5a-2c0071d7b5b3" />

---

## Περιγραφή

Η εφαρμογή επιτρέπει σε καθηγητές και μαθητές να:

Καταγράφουν βιβλία και μέλη της βιβλιοθήκης.
Διαχειρίζονται δανεισμούς και επιστροφές.
Κάνουν αναζήτηση και ταξινόμηση βιβλίων και μελών.
Εξάγουν και εισάγουν δεδομένα σε CSV και Excel αρχεία.
Διατηρούν τα δεδομένα τοπικά, εξασφαλίζοντας ασφάλεια και απόρρητο.

---

## Έμπνευση

Η ιδέα προήλθε από την ανάγκη πολλών σχολείων να έχουν μια απλή, ασφαλή και offline λύση για τη βιβλιοθήκη τους. Πολλές διαδικτυακές υπηρεσίες απαιτούν συνεχή σύνδεση ή εκθέτουν προσωπικά δεδομένα μαθητών. Το SchoolLIB δημιουργήθηκε για να προσφέρει μια καθαρή, τοπική και αξιόπιστη λύση που μπορεί να λειτουργήσει σε κάθε υπολογιστή σχολείου, χωρίς τεχνικές απαιτήσεις.

---

## Τεχνολογίες

- Python 3
- PySide6 (Qt6) για το γραφικό περιβάλλον (GUI)
- SQLite3 για την τοπική βάση δεδομένων
- ReportLab για δημιουργία PDF (κάρτες μελών, εκθέσεις)
- PyMuPDF (fitz) για rendering PDF
- OpenPyXL / xlrd για ανάγνωση Excel αρχείων (.xlsx / .xls)
- qrcode για δημιουργία QR codes στις κάρτες μελών
- pycryptodome για κρυπτογράφηση αντιγράφων ασφαλείας
- requests για ISBN auto-fill (OpenLibrary + Google Books API)

---

## Κύρια Χαρακτηριστικά

| Δυνατότητα | Περιγραφή |
|-------------|------------|
| Καταχώριση βιβλίων | Εύκολη εισαγωγή και διαχείριση τίτλων, συγγραφέων, αντιτύπων |
| Διαχείριση μελών | Εισαγωγή μαθητών και εκπαιδευτικών με μοναδικούς αριθμούς |
| Δανεισμοί | Εύκολη καταγραφή ποιος δανείζεται τι, με υπενθυμίσεις |
| Αναζήτηση | Άμεση αναζήτηση βιβλίων ή μελών με autocomplete |
| ISBN Auto-Fill | Αυτόματη συμπλήρωση στοιχείων βιβλίου από OpenLibrary και Google Books API |
| Εξαγωγή CSV/Excel | Δημιουργία αντιγράφου ασφαλείας ή μεταφοράς δεδομένων |
| Εισαγωγή CSV/Excel | Μαζική προσθήκη βιβλίων ή μελών με drag & drop, auto-mapping και multi-encoding |
| Κάρτες μελών | PDF κάρτες με QR code, στοιχεία μέλους, ημερομηνία έκδοσης |
| Γραφήματα Dashboard | Interactive bar/pie charts με light background και themed χρώματα |
| SVG Icons | Επαγγελματικά εικονίδια σε sidebar, κουμπιά και cards |
| Offline λειτουργία | Όλα τα δεδομένα αποθηκεύονται τοπικά για μέγιστη ασφάλεια |

---

## Εγκατάσταση

```bash
pip install -r requirements.txt
python main.py
```

Για δημιουργία exe:
```bash
build.bat
```

---

## Δομή Εφαρμογής

```
SchoolLIB/
  main.py                 -- Εκκίνηση εφαρμογής
  requirements.txt        -- Εξαρτήσεις
  build.bat               -- Script δημιουργίας exe
  core/
    db.py                 -- Βάση δεδομένων (SQLite, schema v2)
    settings.py           -- Ρυθμίσεις εφαρμογής
    backup.py             -- Αυτόματα αντίγραφα ασφαλείας (κρυπτογραφημένα)
    paths.py              -- Διαδρομές αρχείων
  ui/
    theme.py              -- Χρώματα, QSS styles, font sizes
    icons.py              -- SVG εικονίδια (20+ shapes) + make_icon()
    main_window.py        -- Κύριο παράθυρο με sidebar + stack
    widgets/
      nav_button.py       -- Custom sidebar button με hover/checked transitions
      autocomplete.py     -- Autocomplete combo box (δανεισμοί)
      book_dialog.py      -- Dialog βιβλίου με ISBN auto-fill
      member_dialog.py    -- Dialog μέλους
      loan_dialog.py      -- Dialog δανεισμού/επιστροφής
      dropzone.py         -- Drag & drop widget (εισαγωγή)
      big_buttons.py      -- StatCard/ActionCard widgets
    pages/
      dashboard_page.py   -- Dashboard με stats + charts + quick actions
      books_page.py       -- Κατάλογος βιβλίων
      members_page.py     -- Κατάλογος μελών
      loans_page.py       -- Ενεργοί δανεισμοί + ιστορικό
      calendar_page.py    -- Ημερολόγιο δανεισμών
      organize_page.py    -- Κατηγορίες, εκδόσεις, ράφια
      settings_page.py    -- Ρυθμίσεις εφαρμογής
      import_page.py      -- Μαζική εισαγωγή (single-screen editor)
  services/
    isbn_lookup.py        -- ISBN auto-fill (OpenLibrary + Google, parallel)
    importer.py           -- CSV/Excel import με auto-mapping
    exporter.py           -- CSV/Excel/PDF export
    printing.py           -- PDF generation (κάρτες μελών, εκθέσεις)
```

---

## Official Web Site

https://schoollib.world
---

Copyright (c) Andreas Agouridis
