from __future__ import annotations

from PySide6 import QtWidgets

from ..theme import tokens
from .style_utils import HEADING, MUTED, SECTION_TITLE, set_variant


def _label(text: str, variant: str, parent=None) -> QtWidgets.QLabel:
    return set_variant(QtWidgets.QLabel(text, parent), variant)


def section_title_label(text: str, parent=None) -> QtWidgets.QLabel:
    return _label(text, SECTION_TITLE, parent)


def muted_label(text: str, parent=None) -> QtWidgets.QLabel:
    return _label(text, MUTED, parent)


def heading_label(text: str, parent=None) -> QtWidgets.QLabel:
    return _label(text, HEADING, parent)


def page_title_label(text: str, parent=None) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(text, parent)
    font = label.font()
    font.setPointSize(max(font.pointSize() + tokens.TITLE_FONT_STEP, tokens.TITLE_FONT_MIN))
    font.setBold(True)
    label.setFont(font)
    return label
