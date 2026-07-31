from __future__ import annotations

from PySide6 import QtWidgets

from ..theme import tokens


def themed_dialog(parent, title: str, size: tuple[int, int] = tokens.DIALOG_SIZE) -> QtWidgets.QDialog:
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.resize(*size)
    return dialog


def show_dialog(dialog: QtWidgets.QDialog) -> None:
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()


def close_dialog(dialog: QtWidgets.QDialog | None) -> None:
    if dialog is not None:
        dialog.close()
