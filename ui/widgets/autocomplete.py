from PySide6 import QtCore, QtWidgets


class FilterComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.setMaxVisibleItems(20)
        self._items = []  # list of dicts
        line_edit = self.lineEdit()
        line_edit.textEdited.connect(self._filter)
        self.activated.connect(self._on_activated)

    def set_items(self, items, display_key="title", search_keys=None):
        self._items = items
        self._display_key = display_key
        self._search_keys = search_keys or [display_key]
        self._filter(self.currentText())

    def _filter(self, text):
        self.blockSignals(True)
        self.clear()
        text_l = (text or "").strip().lower()
        count = 0
        for item in self._items:
            haystack = " ".join(str(item.get(k, "")) for k in self._search_keys).lower()
            if text_l and text_l not in haystack:
                continue
            self.addItem(str(item.get(self._display_key, "")), item)
            count += 1
            if count >= 50:
                break
        self.blockSignals(False)

    def _on_activated(self, index):
        item = self.itemData(index)
        if item:
            self.setCurrentText(str(item.get(self._display_key, "")))

    def current_item(self):
        current = self.currentText().strip().lower()
        if not current:
            return None
        best = None
        best_score = None
        for item in self._items:
            positions = []
            for k in self._search_keys:
                pos = str(item.get(k, "")).lower().find(current)
                if pos >= 0:
                    positions.append(pos)
            if not positions:
                continue
            score = min(positions)
            if best_score is None or score < best_score:
                best = item
                best_score = score
        return best

    def clear_items(self):
        self._items = []
        self.clear()