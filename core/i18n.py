import re

from PySide6 import QtCore, QtWidgets


_LANGUAGE = "en"

_ENGLISH = {
    "Αρχική": "Dashboard",
    "Βιβλία": "Books",
    "Μέλη": "Members",
    "Δάνεια": "Loans",
    "Ημερολόγιο": "Calendar",
    "Οργάνωση": "Organization",
    "Ρυθμίσεις": "Settings",
    "SchoolLIB - Διαχείριση Σχολικής Βιβλιοθήκης": "SchoolLIB - School Library Management",
    "Βιβλιοθήκη Σχολείου": "School Library",
    "  Στατιστικά": "  Statistics",
    "Έτοιμο": "Ready",
    "Πρότυπο": "Template",
    "Εξαγωγή καταλόγου": "Export catalog",
    "ΣΥΝΟΠΤΙΚΑ ΣΤΑΤΙΣΤΙΚΑ\n\nΒιβλιοθήκες: ": "LIBRARY OVERVIEW\n\nLibraries: ",
    "\nΒιβλία (τίτλοι): ": "\nBooks (titles): ",
    "\nΑντίτυπα: ": "\nCopies: ",
    "\nΜέλη: ": "\nMembers: ",
    "\nΡάφια/τοποθεσίες: ": "\nShelves/locations: ",
    "\nΚατηγορίες: ": "\nCategories: ",
    "\nΕνεργά δάνεια: ": "\nActive loans: ",
    "\nΣυνολικοί δανεισμοί: ": "\nTotal loans: ",
    "\nΚαθυστερημένα: ": "\nOverdue: ",
    "\nΛήγουν άμεσα: ": "\nDue soon: ",
    "\n\nΔΗΜΟΦΙΛΕΣΤΕΡΑ ΒΙΒΛΙΑ\n": "\n\nMOST BORROWED BOOKS\n",
    "\n- Κανένα δάνειο ακόμη -": "\n- No loans yet -",
    "Στατιστικά": "Statistics",
    "Το πρότυπο αποθηκεύτηκε.": "The template was saved.",
    "Εξαγωγή": "Export",
    "Δεν υπάρχουν βιβλία.": "No books found.",
    "Πλήρης Κατάλογος": "Full catalog",
    "Ο πλήρης κατάλογος εξήχθη: ": "The full catalog was exported: ",
    "Πρότυπο Βιβλίων": "Books template",
    " δανεισμοί": " loans",
    "Αναζήτηση τίτλου, συγγραφέα, ISBN ή αριθμού βιβλίου": "Search title, author, ISBN, or book number",
    " Προσθήκη βιβλίου": " Add book",
    " Επεξεργασία": " Edit",
    " Διαγραφή": " Delete",
    " Δανεισμός": " Lend",
    " Εκτύπωση ετικετών": " Print labels",
    " Εξαγωγή": " Export",
    " Εισαγωγή": " Import",
    "Όλες οι βιβλιοθήκες": "All libraries",
    "Όλες οι κατηγορίες": "All categories",
    "Όλα τα ράφια": "All shelves",
    "Όλες οι ετικέτες": "All tags",
    "Αποθήκευση ετικετών": "Save labels",
    "Εξαγωγή βιβλίων": "Export books",
    "Βιβλιοθήκη:": "Library:",
    "Κατηγορία:": "Category:",
    "Ράφι:": "Shelf:",
    "Ετικέτα:": "Tag:",
    "Τίτλος": "Title",
    "Συγγραφέας": "Author",
    "Αριθμός": "Number",
    "Αντίτυπα": "Copies",
    "Διαθέσιμα": "Available",
    "Τοποθεσία": "Location",
    "Κατηγορίες": "Categories",
    "Έτος": "Year",
    " αποτελέσματα": " results",
    "Επιλέξτε πρώτα ένα βιβλίο.": "Select a book first.",
    "Οι αλλαγές αποθηκεύτηκαν.": "Changes saved.",
    "Επιλέξτε πρώτα βιβλία.": "Select books first.",
    "Διαγραφή": "Delete",
    "Εκτύπωση": "Print",
    "Δεν υπάρχουν βιβλία για εκτύπωση.": "No books to print.",
    "Δεν υπάρχουν βιβλία προς εξαγωγή.": "No books to export.",
    "Πιθανό διπλότυπο": "Possible duplicate",
    "Παρόμοιο βιβλίο υπάρχει ήδη στον κατάλογο.\nΘέλετε να το προσθέσετε ούτως ή άλλως?": "A similar book already exists in the catalog.\nDo you want to add it anyway?",
    "Το βιβλίο προστέθηκε.": "Book added.",
    "Σφάλμα": "Error",
    "Όριο δανεισμού": "Loan limit",
    "Ημερολόγιο Προθεσμιών": "Due date calendar",
    "Δάνεια της ημέρας": "Loans for this day",
    "Εξαγωγή ημέρας": "Export day",
    "Η εξαγωγή ολοκληρώθηκε.": "Export complete.",
    "Δεν υπάρχουν δάνεια για αυτή την ημέρα.": "There are no loans for this day.",
    "Δεν υπάρχουν δάνεια για αυτήν την ημέρα.": "There are no loans for this day.",
    "Υπερημερία": "Overdue",
    "Κανονικό": "On time",
    "Δημοφιλέστερα βιβλία": "Most borrowed books",
    "Κατανομή κατηγοριών": "Category breakdown",
    "Προσοχή": "Attention",
    "Βιβλία στους καταλόγους": "Books in catalog",
    "Ενεργά δάνεια": "Active loans",
    "Καθυστερημένες επιστροφές": "Overdue returns",
    "Δανεισμός βιβλίου": "Lend a book",
    "Καταχώρηση νέου δανείου": "Create a new loan",
    "Προσθήκη βιβλίου": "Add a book",
    "Νέο βιβλίο στον κατάλογο": "Add a book to the catalog",
    "Προσθήκη μέλους": "Add a member",
    "Εγγραφή νέου μέλους": "Register a new member",
    "Υπενθυμίσεις": "Reminders",
    "Ληγμένα και επικείμενα δάνεια": "Overdue and upcoming loans",
    "Δανεισμοί": "Loans",
    "Παράταση": "Extend",
    "Παρόμοιο βιβλίο υπάρχει ήδη στον κατάλογο.\nΘέλετε να το προσθέσετε ούτως ή άλλως;": "A similar book already exists in the catalog.\nDo you want to add it anyway?",
    "Χωρίς κατηγορίες": "No categories",
    "Δεν υπάρχουν εκκρεμότητες. Όλα είναι εντάξει.": "No outstanding items. Everything is up to date.",
    "Τίτλος *": "Title *",
    "Αριθμός βιβλίου": "Book number",
    "Εκδότης": "Publisher",
    "Έκδοση": "Edition",
    "Σελίδες": "Pages",
    "Σημειώσεις": "Notes",
    "Ετικέτες": "Tags",
    "Ράφι/Τοποθεσία": "Shelf/location",
    "Όνομα *": "Name *",
    "Αριθμός μέλους": "Member number",
    "Τάξη": "Class",
    "Τηλέφωνο": "Phone",
    "Κωδικός μέλους *": "Member ID *",
    "Κωδικός βιβλίου *": "Book ID *",
    "Ημερομηνία δανεισμού": "Loan date",
    "Προθεσμία": "Due date",
    "Επιστροφή": "Return",
    "Ανανεώσεις": "Renewals",
    "Εισαγωγή από αρχείο": "Import from file",
    " Λήψη προτύπου": " Download template",
    " Καθαρό": " Clear",
    "Παράλειψη διπλοτύπων": "Skip duplicates",
    "Ενημέρωση υπαρχόντων": "Update existing",
    " Καταχώρηση δεδομένων": " Import data",
    " Νέα εισαγωγή": " New import",
    "Αντιστοίχιση στηλών": "Map columns",
    "Αλλάξτε εάν χρειαστεί. Τα πεδία με * είναι υποχρεωτικά.": "Adjust if needed. Fields marked * are required.",
    "(να αγνοηθεί)": "(ignore)",
    "Αντιστοίχιση": "Mapping",
    "Χωρίς σφάλματα — όλα καταχωρήθηκαν.": "No errors — everything was imported.",
    "Σφάλμα εισαγωγής": "Import error",
    "Αναζήτηση σε βιβλία ή μέλη": "Search books or members",
    " Νέος δανεισμός": " New loan",
    " Επιστροφή": " Return",
    " Παράταση": " Extend",
    " Εκτύπωση υπενθυμίσεων": " Print reminders",
    "Ενεργά Δάνεια": "Active loans",
    "Όλα": "All",
    "Μόνο ενεργά": "Active only",
    "Μόνο επιστραφέντα": "Returned only",
    " Διαγραφή επιλεγμένου": " Delete selected",
    "Ιστορικό Δανείων": "Loan history",
    "Βιβλίο": "Book",
    "Μέλος": "Member",
    "Δανείστηκε": "Borrowed",
    "Υπόλοιπο": "Remaining",
    "Τύπος:": "Type:",
    "Από:": "From:",
    "Έως:": "To:",
    "Ημερομηνία": "Date",
    "Ληξιπρόθεσμο": "Overdue",
    "Επιστροφή Βιβλίου": "Return book",
    "Παράταση Δανείου": "Extend loan",
    "Ημέρες παράτασης:": "Extension days:",
    "Αποθήκευση υπενθυμίσεων": "Save reminders",
    "Εξαγωγή δανείων": "Export loans",
    "Εξαγωγή ιστορικού": "Export history",
    "Το βιβλίο επιστράφηκε.": "Book returned.",
    "Δεν υπάρχουν ληξιπρόθεσμα ή επικείμενα δάνεια.": "There are no overdue or upcoming loans.",
    "Δεν υπάρχουν δάνεια.": "No loans found.",
    "Δεν υπάρχουν εγγραφές.": "No records found.",
    "Ιστορικό": "History",
    "Επιλέξτε εγγραφές.": "Select records.",
    "Λήγει σήμερα": "Due today",
    "Λήγει σύντομα": "Due soon",
    "Αναζήτηση ονοματεπωνύμου ή αριθμού μέλους": "Search name or member number",
    "Όλες οι τάξεις": "All classes",
    " Προσθήκη μέλους": " Add member",
    " Εκτύπωση καρτελών": " Print cards",
    "Τα μέλη διαγράφηκαν.": "Members deleted.",
    "Αποθήκευση καρτελών": "Save cards",
    "Εξαγωγή μελών": "Export members",
    "Τάξη:": "Class:",
    "Ονοματεπώνυμο": "Full name",
    "Το μέλος προστέθηκε.": "Member added.",
    "Επιλέξτε πρώτα ένα μέλος.": "Select a member first.",
    "Επιλέξτε πρώτα μέλη.": "Select members first.",
    "Δεν γίνεται": "Not allowed",
    " έχει ενεργά δάνεια.": " has active loans.",
    " μέλη.": " members.",
    "Οργάνωση - Φάκελοι": "Organization",
    "Δημιουργήστε βιβλιοθήκες, ράφια (αίθουσα, ντουλάπα, ράφι) και κατηγορίες. Αναθέστε βιβλία στα ράφια μαζικά.": "Create libraries, shelves, and categories. Assign books to shelves in bulk.",
    "Βιβλιοθήκες": "Libraries",
    "Προσθήκη": "Add",
    "Μετονομασία": "Rename",
    "Ράφια και Τοποθεσίες": "Shelves and locations",
    "Νέο ράφι": "New shelf",
    "Μετακίνηση": "Move",
    "Νέα κατηγορία": "New category",
    "Δημοφιλείς Ετικέτες": "Popular tags",
    "Ανάθεση βιβλίων σε ράφι": "Assign books to shelf",
    "Αναζήτηση βιβλίων": "Search books",
    " Ανάθεση στο επιλεγμένο ράφι": " Assign to selected shelf",
    " Απομάκρυνση από ράφι": " Remove from shelf",
    " Ανανέωση": " Refresh",
    "Εισαγωγή / Εξαγωγή": "Import / export",
    " Πρότυπο Excel": " Excel template",
    " Οδηγός Εισαγωγής": " Import wizard",
    " Εξαγωγή πλήρους καταλόγου": " Export full catalog",
    "Όνομα ραφιού (π.χ. Ντουλάπα 1, Ράφι 2):": "Shelf name (e.g. Cabinet 1, Shelf 2):",
    "Νέο όνομα:": "New name:",
    "Μετακίνηση ραφιού": "Move shelf",
    "Άκυρο": "Cancel",
    "Τα βιβλία απομακρύνθηκαν από το ράφι.": "Books removed from shelf.",
    "Νέα βιβλιοθήκη": "New library",
    "Όνομα βιβλιοθήκης:": "Library name:",
    "Διαγραφή βιβλιοθήκης και όλων των δεδομένων της?": "Delete this library and all its data?",
    "Τρέχοντα ράφια": "Current shelves",
    "Μεταφέρετε εύκολα καταλόγους από άλλα προγράμματα ή Excel. Κατεβάστε πρότυπο αρχείο, συμπληρώστε και εισάγετε.": "Import catalogs from other programs or Excel using the downloadable template.",
    "Ράφια": "Shelves",
    "Επιλέξτε πρώτα ράφι.": "Select a shelf first.",
    "(Κορυφή)": "(Top level)",
    "Ανάθεση": "Assign",
    "Επιλέξτε πρώτα ένα ράφι στα αριστερά.": "Select a shelf on the left first.",
    "Επιλέξτε βιβλία από τον πίνακα.": "Select books from the table.",
    "Απομάκρυνση": "Remove",
    "Επιλέξτε ράφι και βιβλία.": "Select a shelf and books.",
    "Επιλέξτε κατηγορία.": "Select a category.",
    "Γενικές Ρυθμίσεις": "General settings",
    "Όνομα σχολείου / βιβλιοθήκης:": "School / library name:",
    "Προθεσμία δανεισμού (ημέρες):": "Loan period (days):",
    "Μέγιστο δανεισμένο βιβλίων ανά μέλος:": "Maximum loans per member:",
    "Προειδοποίηση X ημέρες πριν λήξει:": "Reminder days before due date:",
    "Μεγάλα γράμματα": "Large text",
    "Πολύ μεγάλα γράμματα": "Extra large text",
    "Μέγεθος γραμματοσειράς:": "Text size:",
    " Αποθήκευση γενικών ρυθμίσεων": " Save general settings",
    "Αντίγραφα ασφαλείας (Backup)": "Backups",
    "Αυτόματο backup κατά το κλείσιμο": "Back up automatically on exit",
    "Αφήστε κενό για μη κρυπτογραφημένο backup": "Leave blank for an unencrypted backup",
    "Κωδικός backup:": "Backup password:",
    "Να διατηρούνται τα τελευταία:": "Keep the most recent:",
    " Δημιουργία backup τώρα": " Create backup now",
    " Επαναφορά από backup": " Restore from backup",
    "Οι ρυθμίσεις αποθηκεύτηκαν.": "Settings saved.",
    "Επιλογή backup": "Select backup",
    "Backup (*.enc *.db);;Όλα (*)": "Backup (*.enc *.db);;All files (*)",
    "Επαναφορά": "Restore",
    "Προσοχή: τα τρέχοντα δεδομένα θα αντικατασταθούν.\nΘέλετε να συνεχίσετε?": "Warning: current data will be replaced.\nDo you want to continue?",
    "Δεν ήταν δυνατή η δημιουργία backup.": "Could not create a backup.",
    "Επαναφορά ολοκληρώθηκε.": "Restore complete.",
    "Η επαναφορά ολοκληρώθηκε.": "Restore completed.",
    "Κωδικός": "Password",
    "Δώστε τον κωδικό του backup:": "Enter the backup password:",
    "Αριθμός βιβλίου:": "Book number:",
    "Αυτόματη συμπλήρωση από ISBN": "Auto-fill from ISBN",
    "Τίτλος *:": "Title *:",
    "Συγγραφέας:": "Author:",
    "Εκδότης:": "Publisher:",
    "Έκδοση / Έτος / Σελίδες / Αντίτυπα:": "Edition / year / pages / copies:",
    "Ταξιθετικός (Dewey):": "Dewey classification:",
    "Νέα κατηγορία + Enter": "New category + Enter",
    "Κατηγορίες:": "Categories:",
    "π.χ. ελληνική λογοτεχνία, μυθιστόρημα": "e.g. fiction, mystery",
    "Ετικέτες (κόμμα):": "Tags (comma-separated):",
    "Ράφια:": "Shelves:",
    "Σημειώσεις:": "Notes:",
    "Αποθήκευση": "Save",
    "Αναζήτηση...": "Search...",
    "Γίνεται αναζήτηση στο διαδίκτυο...": "Searching online...",
    "Επεξεργασία Βιβλίου": "Edit book",
    "Προσθήκη Βιβλίου": "Add book",
    "Συμπληρώστε πρώτα ISBN.": "Enter an ISBN first.",
    "Τα στοιχεία συμπληρώθηκαν από το διαδίκτυο.": "Book details filled in from the web.",
    "Δεν βρέθηκαν στοιχεία για αυτό το ISBN.": "No details found for this ISBN.",
    "Χρονικό": "Timeout",
    "Η αναζήτηση άργησε να απαντήσει. Ελέγξτε το διαδίκτυο και δοκιμάστε ξανά.": "The search timed out. Check your connection and try again.",
    "Δεν υπάρχει σύνδεση στο διαδίκτυο. Συμπληρώστε τα στοιχεία χειροκίνητα.": "No internet connection. Enter the details manually.",
    "Αποτυχία αναζήτησης. Συμπληρώστε τα στοιχεία χειροκίνητα.": "Search failed. Enter the details manually.",
    "Ο τίτλος είναι υποχρεωτικός.": "A title is required.",
    "Σύρετε και αφήστε το αρχείο εδώ": "Drag and drop a file here",
    "Επιλογή αρχείου": "Choose file",
    "Δανεισμός Βιβλίου": "Lend a book",
    "Μέλος:": "Member:",
    "Βιβλίο:": "Book:",
    "Ημέρες δανεισμού:": "Loan period (days):",
    "Δανεισμός": "Lend",
    "Επιλέξτε μέλος και βιβλίο για να ολοκληρωθεί ο δανεισμός:": "Select a member and book to complete the loan:",
    "Επιλέξτε μέλος.": "Select a member.",
    "Επιλέξτε βιβλίο.": "Select a book.",
    "Επιλέξτε δάνειο": "Select loan",
    "ΟΚ": "OK",
    "Δεν υπάρχουν ενεργά δάνεια.": "No active loans.",
    "Επιλέξτε δάνειο από τη λίστα:": "Select a loan from the list:",
    "Αριθμός μέλους:": "Member number:",
    "Ονοματεπώνυμο *:": "Full name *:",
    "Τάξη / Τμήμα:": "Class / group:",
    "Τηλέφωνο:": "Phone:",
    "Επεξεργασία Μέλους": "Edit member",
    "Προσθήκη Μέλους": "Add member",
    "Το όνομα είναι υποχρεωτικό.": "A name is required.",
    "Αναζήτηση": "Search",
    "ΣΥΝΟΠΤΙΚΑ ΣΤΑΤΙΣΤΙΚΑ": "LIBRARY OVERVIEW",
    "Βιβλιοθήκες": "Libraries",
    "Βιβλία (τίτλοι)": "Books (titles)",
    "Μέλη": "Members",
    "Ράφια/τοποθεσίες": "Shelves/locations",
    "Συνολικοί δανεισμοί": "Total loans",
    "Καθυστερημένα": "Overdue",
    "Λήγουν άμεσα": "Due soon",
    "ΔΗΜΟΦΙΛΕΣΤΕΡΑ ΒΙΒΛΙΑ": "MOST BORROWED BOOKS",
    "Κανένα δάνειο ακόμη": "No loans yet",
    "Ελληνικά": "Greek",
    "δανεισμοί": "loans",
    "Δάνεια ": "Loans ",
    "Δεν υπάρχουν μέλη.": "No members found.",
    "Οι κουκκίδες δείχνουν πόσες επιστροφές λήγουν κάθε μέρα. Κόκκινη σημαίνει ότι κάποια έχουν ήδη λήξει.": "Dots show how many books are due each day. Red indicates overdue returns.",
    "Σύρετε εύκολα βιβλία, μέλη και δάνεια από Excel, CSV ή από άλλα προγράμματα. Ο οδηγός αναγνωρίζει μόνος του τις στήλες και σας ζητάει να επιβεβαιώσετε.": "Import books, members, and loans from Excel, CSV, or other programs. The wizard detects columns and lets you confirm them.",
    "(χωρίς επικεφαλίδες)": "(no headers)",
    "Ορίστε τις υποχρεωτικές στήλες: ": "Map the required columns: ",
    "Δεν ήταν δυνατό να ανοιχτεί:\n": "Could not open:\n",
    "Διαγραφή βιβλιοθήκης και όλων των δεδομένων της;": "Delete this library and all its data?",
    "Προσοχή: τα τρέχοντα δεδομένα θα αντικατασταθούν.\nΘέλετε να συνεχίσετε;": "Warning: current data will be replaced.\nDo you want to continue?",
    "Οι υπηρεσίες είναι προσωρινά απασχολημένες (429). Δοκιμάστε ξανά σε λίγο ή συμπληρώστε τα στοιχεία χειροκίνητα.": "The service is temporarily busy (429). Try again later or enter the details manually.",
    "Χρονικό όριο (timeout) — η αναζήτηση άργησε να απαντήσει.": "Timeout — the search took too long to respond.",
    "ή πατήστε μέσα στη ζώνη για να επιλέξετε αρχείο από τον υπολογιστή\n(Excel .xlsx, .xls ή .csv)": "or click here to choose a file\n(Excel .xlsx, .xls, or .csv)",
    "Αρχεία δεδομένων (*.xlsx *.xls *.csv);;Όλα τα αρχεία (*)": "Data files (*.xlsx *.xls *.csv);;All files (*)",
    "Έναρξη": "Get started",
    "Καλώς ορίσατε στο SchoolLIB": "Welcome to SchoolLIB",
    "Ας ρυθμίσουμε τη σχολική σας βιβλιοθήκη.": "Let's set up your school library.",
    "Γλώσσα εφαρμογής:": "App language:",
    "Στοιχεία σχολείου": "School details",
    "Όνομα σχολείου *": "School name *",
    "Χώρα *": "Country *",
    "Πόλη / διεύθυνση": "City / address",
    "Υπεύθυνος βιβλιοθήκης": "Librarian / contact",
    "Συμπληρώστε το όνομα του σχολείου και τη χώρα.": "Enter the school name and country to continue.",
}

_GREEK = {translation: source for source, translation in _ENGLISH.items()}
_GREEK.update({
    "School profile": "Στοιχεία σχολείου",
    "School name *:": "Όνομα σχολείου *:",
    "Country *:": "Χώρα *:",
    "City / address:": "Πόλη / διεύθυνση:",
    "Phone:": "Τηλέφωνο:",
    "Email:": "Email:",
    "Librarian / contact:": "Υπεύθυνος βιβλιοθήκης:",
    "App language:": "Γλώσσα εφαρμογής:",
    " Save school profile": " Αποθήκευση στοιχείων σχολείου",
    "Enter the school name and country to continue.": "Συμπληρώστε το όνομα του σχολείου και τη χώρα.",
    "School profile saved.": "Τα στοιχεία του σχολείου αποθηκεύτηκαν.",
    "School profile saved. Restart the app to apply the language change.": "Τα στοιχεία αποθηκεύτηκαν. Κάντε επανεκκίνηση της εφαρμογής για να εφαρμοστεί η γλώσσα.",
    "English": "Αγγλικά",
    "Greek": "Ελληνικά",
    "School details": "Στοιχεία σχολείου",
    "App language:": "Γλώσσα εφαρμογής:",
    "School name *": "Όνομα σχολείου *",
    "Country *": "Χώρα *",
    "City / address": "Πόλη / διεύθυνση",
    "Librarian / contact": "Υπεύθυνος βιβλιοθήκης",
    "Get started": "Έναρξη",
    "Welcome to SchoolLIB": "Καλώς ορίσατε στο SchoolLIB",
    "Let's set up your school library.": "Ας ρυθμίσουμε τη σχολική σας βιβλιοθήκη.",
    "Enter the school name and country to continue.": "Συμπληρώστε το όνομα του σχολείου και τη χώρα.",
})

_DYNAMIC = (
    (re.compile(r"^Συνολικά (\d+) αντίτυπα$"), r"\1 copies total"),
    (re.compile(r"^Σε (\d+) βιβλιοθήκες$"), r"Across \1 libraries"),
    (re.compile(r"^Συνολικά (\d+) δανεισμοί$"), r"\1 loans total"),
    (re.compile(r"^Δάνεια (.+)$"), r"Loans \1"),
    (re.compile(r"^(\d+) λήγουν σύντομα$"), r"\1 due soon"),
    (re.compile(r"^Kαθυστερημένο: (.+) -> (.+) \(λόγω (.+), υπερημερία (\d+) ημ\.\)$"),
     r"Overdue: \1 -> \2 (due \3, \4 days late)"),
    (re.compile(r"^Λήγει σύντομα: (.+) -> (.+) \(σ (.+)\)$"),
     r"Due soon: \1 -> \2 (due \3)"),
    (re.compile(r"^Διαγράφηκαν (\d+) βιβλία\.$"), r"\1 books deleted."),
    (re.compile(r"^Διαγράφηκαν (\d+) μέλη\.$"), r"\1 members deleted."),
    (re.compile(r"^Διαγράφηκαν (\d+) εγγραφές\.$"), r"\1 records deleted."),
    (re.compile(r"^Εξήχθησαν (\d+) βιβλία\.$"), r"\1 books exported."),
    (re.compile(r"^Εξήχθησαν (\d+) δάνεια\.$"), r"\1 loans exported."),
    (re.compile(r"^Εξήχθησαν (\d+) εγγραφές\.$"), r"\1 records exported."),
    (re.compile(r"^Δημιουργήθηκαν (\d+) ετικέτες: (.+)$"), r"\1 labels created: \2"),
    (re.compile(r"^Δημιουργήθηκαν (\d+) καρτέλες: (.+)$"), r"\1 cards created: \2"),
    (re.compile(r"^Δημιουργήθηκαν υπενθυμίσεις για (\d+) δάνεια\.$"),
     r"Reminders created for \1 loans."),
    (re.compile(r"^Ανατέθηκαν (\d+) βιβλία στο ράφι\.$"), r"\1 books assigned to the shelf."),
    (re.compile(r"^Το μέλος (.+) έχει ενεργά δάνεια\.$"), r"\1 has active loans."),
    (re.compile(r"^(\d+) αποτελέσματα$"), r"\1 results"),
    (re.compile(r"^Υπολείπονται (\d+) ημέρες$"), r"\1 days remaining"),
    (re.compile(r"^Παράταση έως (.+)$"), r"Extended until \1"),
    (re.compile(r"^Δανεισμός ολοκληρώθηκε, προθεσμία (.+)\.?$"), r"Loan created, due \1"),
    (re.compile(r"^Backup δημιουργήθηκε: (.+)$"), r"Backup created: \1"),
    (re.compile(r"^Το backup αποθηκεύτηκε:\n(.+)$"), r"Backup saved:\n\1"),
    (re.compile(r"^(.+): (\d+) εισήχθηκαν, (\d+) ενημερώθηκαν, (\d+) παραλείφθηκαν\.$"),
     r"\1: \2 imported, \3 updated, \4 skipped."),
    (re.compile(r"^Διαγραφή (\d+) βιβλίου/ων και του ιστορικού δανεισμού τους;$"),
     r"Delete \1 book(s) and their loan histories?"),
    (re.compile(r"^Διαγραφή (\d+) μέλους/ων;$"), r"Delete \1 member(s)?"),
    (re.compile(r"^Διαγραφή (\d+) εγγραφών ιστορικού;$"), r"Delete \1 history record(s)?"),
    (re.compile(r"^Διαγραφή ραφιού '(.+)' και τυχόν υποφακέλων;$"),
     r"Delete shelf '\1' and any sub-shelves?"),
    (re.compile(r"^Διαγραφή κατηγορίας '(.+)'$"), r"Delete category '\1'"),
    (re.compile(r"^Μετακίνηση του '(.+)' κάτω από:$"), r"Move '\1' under:"),
    (re.compile(r"^Το μέλος έχει φτάσει το όριο δανεισμού \((\d+) βιβλία\)\.$"),
     r"The member has reached the loan limit (\1 books)."),
    (re.compile(r"^Το μέλος έχει φτάσει το όριο \((\d+)\)\.?$"),
     r"The member has reached the limit (\1)."),
    (re.compile(r"^(\d+) γραμμές\.$"), r"\1 rows."),
    (re.compile(r"^Μέλος: (\d+) ενεργά δάνεια$"), r"Member: \1 active loans"),
    (re.compile(r"^Βιβλίο: (\d+) διαθέσιμα αντίτυπα$"), r"Book: \1 available copies"),
    (re.compile(r"^\s+\(προθεσμία (.+), υπόλοιπο (\d+) ημέρες\)$"),
     r"  (due \1, \2 days remaining)"),
    (re.compile(r"^  \(προθεσμία (.+)\)$"), r"  (due \1)"),
    (re.compile(r"^(.+)  \[(.+)\] -> (.+)  \(προθεσμία (.+), υπόλοιπο (-?\d+) ημέρες\)$"),
     r"\1 [\2] -> \3  (due \4, \5 days remaining)"),
    (re.compile(r"^(.+) -> (.+)  \(προθεσμία (.+)\)$"), r"\1 -> \2  (due \3)"),
)


def set_language(language):
    global _LANGUAGE
    _LANGUAGE = "el" if language == "el" else "en"


def language():
    return _LANGUAGE


def tr(text):
    if not isinstance(text, str):
        return text
    if _LANGUAGE == "el":
        return _GREEK.get(text, text)
    if text in _ENGLISH:
        return _ENGLISH[text]
    for pattern, replacement in _DYNAMIC:
        if pattern.match(text):
            return pattern.sub(replacement, text)
    return text


def _widget_text(widget):
    if isinstance(widget, QtWidgets.QLabel):
        return widget.text(), widget.setText
    if isinstance(widget, QtWidgets.QAbstractButton):
        return widget.text(), widget.setText
    if isinstance(widget, QtWidgets.QGroupBox):
        return widget.title(), widget.setTitle
    if isinstance(widget, QtWidgets.QWidget):
        title = widget.windowTitle()
        if title:
            return title, widget.setWindowTitle
    return None, None


def translate_widget_tree(widget):
    if widget is None:
        return
    text, setter = _widget_text(widget)
    if text is not None:
        translated = tr(text)
        if translated != text:
            setter(translated)

    if isinstance(widget, QtWidgets.QLineEdit):
        placeholder = widget.placeholderText()
        translated = tr(placeholder)
        if translated != placeholder:
            widget.setPlaceholderText(translated)
    if isinstance(widget, QtWidgets.QComboBox):
        for index in range(widget.count()):
            item_text = widget.itemText(index)
            translated = tr(item_text)
            if translated != item_text:
                widget.setItemText(index, translated)
    if isinstance(widget, QtWidgets.QTabWidget):
        for index in range(widget.count()):
            tab_text = widget.tabText(index)
            translated = tr(tab_text)
            if translated != tab_text:
                widget.setTabText(index, translated)
    if isinstance(widget, QtWidgets.QTableWidget):
        for index in range(widget.columnCount()):
            header = widget.horizontalHeaderItem(index)
            if header is not None:
                header.setText(tr(header.text()))
    if isinstance(widget, QtWidgets.QListWidget) and widget.objectName() in {
        "alertsList", "calendarLoansList", "activeLoanPicker"
    }:
        for index in range(widget.count()):
            item = widget.item(index)
            item.setText(tr(item.text()))
    for child in widget.findChildren(QtWidgets.QWidget):
        text, setter = _widget_text(child)
        if text is not None:
            translated = tr(text)
            if translated != text:
                setter(translated)
        if isinstance(child, QtWidgets.QLineEdit):
            child.setPlaceholderText(tr(child.placeholderText()))
        if isinstance(child, QtWidgets.QComboBox):
            for index in range(child.count()):
                child.setItemText(index, tr(child.itemText(index)))
        if isinstance(child, QtWidgets.QTabWidget):
            for index in range(child.count()):
                child.setTabText(index, tr(child.tabText(index)))
        if isinstance(child, QtWidgets.QTableWidget):
            for index in range(child.columnCount()):
                header = child.horizontalHeaderItem(index)
                if header is not None:
                    header.setText(tr(header.text()))
        if isinstance(child, QtWidgets.QListWidget) and child.objectName() in {
            "alertsList", "calendarLoansList", "activeLoanPicker"
        }:
            for index in range(child.count()):
                item = child.item(index)
                item.setText(tr(item.text()))


class _TranslationFilter(QtCore.QObject):
    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Show:
            QtCore.QTimer.singleShot(0, lambda target=watched: translate_widget_tree(target))
        elif event.type() == QtCore.QEvent.Paint:
            text, setter = _widget_text(watched)
            if text is not None:
                translated = tr(text)
                if translated != text:
                    setter(translated)
        return False


def install(app):
    translator = _TranslationFilter(app)
    app.installEventFilter(translator)
    app._schoollib_translation_filter = translator
