from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ..theme import tokens

ALIGNMENTS = {
    tokens.ALIGN_LEFT: QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
    tokens.ALIGN_CENTER: QtCore.Qt.AlignCenter,
    tokens.ALIGN_RIGHT: QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter,
}

RESIZE_MODES = {
    tokens.RESIZE_FIXED: QtWidgets.QHeaderView.Fixed,
    tokens.RESIZE_STRETCH: QtWidgets.QHeaderView.Stretch,
    tokens.RESIZE_CONTENTS: QtWidgets.QHeaderView.ResizeToContents,
}


def titles(columns) -> tuple[str, ...]:
    return tuple(title for _key, title, _resize, _align in columns)


def keys(columns) -> tuple[str, ...]:
    return tuple(key for key, _title, _resize, _align in columns)


def alignment(columns, section: int):
    return ALIGNMENTS.get(columns[section][3])


def configure_header(view: QtWidgets.QTableView, columns, fixed_widths: dict | None = None) -> None:
    header = view.horizontalHeader()
    header.setStretchLastSection(False)
    header.setHighlightSections(False)
    for section, (key, _title, resize, _align) in enumerate(columns):
        header.setSectionResizeMode(section, RESIZE_MODES[resize])
        width = (fixed_widths or {}).get(key)
        if width:
            header.resizeSection(section, int(width))
    view.verticalHeader().setVisible(False)
