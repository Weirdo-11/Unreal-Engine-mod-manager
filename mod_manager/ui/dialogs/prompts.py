from __future__ import annotations

from PySide6 import QtGui, QtWidgets


def show_error(parent, title: str, message: str) -> None:
    QtWidgets.QMessageBox.critical(parent, title, message)


def show_warning(parent, title: str, message: str) -> None:
    QtWidgets.QMessageBox.warning(parent, title, message)


def show_info(parent, title: str, message: str) -> None:
    QtWidgets.QMessageBox.information(parent, title, message)


def ask_yes_no(parent, title: str, message: str) -> bool:
    answer = QtWidgets.QMessageBox.question(
        parent,
        title,
        message,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
    )
    return answer == QtWidgets.QMessageBox.Yes


def choose_directory(parent, title: str) -> str:
    return QtWidgets.QFileDialog.getExistingDirectory(parent, title)


def choose_files(parent, title: str, file_filter: str = "") -> list[str]:
    paths, _selected = QtWidgets.QFileDialog.getOpenFileNames(parent, title, "", file_filter)
    return list(paths)


def choose_open_file(parent, title: str, file_filter: str = "") -> str:
    path, _selected = QtWidgets.QFileDialog.getOpenFileName(parent, title, "", file_filter)
    return path


def choose_color(parent, current: QtGui.QColor, title: str) -> QtGui.QColor:
    return QtWidgets.QColorDialog.getColor(current, parent, title)
