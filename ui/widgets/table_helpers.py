from PySide6 import QtCore, QtGui, QtWidgets


def make_table(headers, object_name="table"):
    table = QtWidgets.QTableWidget()
    table.setObjectName(object_name)
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)
    table.setShowGrid(True)
    table.setSortingEnabled(True)
    return table


def fill_table(table, rows, columns, hidden_cols=None):
    hidden_cols = hidden_cols or []
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, key in enumerate(columns):
            val = row.get(key, "")
            item = QtWidgets.QTableWidgetItem("" if val is None else str(val))
            item.setData(QtCore.Qt.UserRole, row)
            table.setItem(r, c, item)
    for c in hidden_cols:
        table.setColumnHidden(c, True)
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def row_data(table, row):
    if row < 0:
        return None
    item = table.item(row, 0)
    return item.data(QtCore.Qt.UserRole) if item else None


def selected_data(table):
    rows = set(index.row() for index in table.selectedIndexes())
    return [row_data(table, r) for r in sorted(rows) if row_data(table, r)]


class SearchBar(QtWidgets.QWidget):
    text_changed = QtCore.Signal(str)
    search_requested = QtCore.Signal()

    def __init__(self, placeholder="Αναζήτηση...", parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QtWidgets.QLineEdit()
        self.edit.setObjectName("search")
        self.edit.setPlaceholderText(placeholder)
        self.edit.setClearButtonEnabled(True)
        self.edit.textChanged.connect(self.text_changed)
        self.edit.returnPressed.connect(self.search_requested)
        layout.addWidget(self.edit, 1)
        self.btn = QtWidgets.QPushButton("Αναζήτηση")
        self.btn.clicked.connect(self.search_requested)
        layout.addWidget(self.btn)

    def text(self):
        return self.edit.text()

    def setText(self, value):
        self.edit.setText(value)