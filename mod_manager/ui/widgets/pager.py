from __future__ import annotations

from PySide6 import QtWidgets

PAGE_LABEL = "Page {page}/{pages}"


def page_text(page: int, pages: int) -> str:
    return PAGE_LABEL.format(page=page, pages=pages)


class PageLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(page_text(1, 1), parent)

    def set_page(self, page: int, pages: int) -> None:
        self.setText(page_text(page, pages))
