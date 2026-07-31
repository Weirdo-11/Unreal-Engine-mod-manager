from __future__ import annotations

from PySide6 import QtCore

from ...models import ModItem
from ..theme import tokens
from . import columns

COLUMNS = tokens.BROKEN_COLUMNS
HEADERS = columns.titles(COLUMNS)


class BrokenTableModel(QtCore.QAbstractTableModel):
    HEADERS = HEADERS
    COLUMNS = COLUMNS

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mods: list[ModItem] = []

    def set_data(self, mods: list[ModItem]) -> None:
        self.beginResetModel()
        self.mods = list(mods)
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.mods)

    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.COLUMNS)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
            return self.HEADERS[section]
        return None

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        mod = self.mods[index.row()]
        if role == QtCore.Qt.UserRole:
            return mod
        if role == QtCore.Qt.DisplayRole:
            return mod.name if index.column() == 0 else str(mod.dest)
        return None
