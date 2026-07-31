from __future__ import annotations

from typing import Callable

from PySide6 import QtGui, QtWidgets

from ...settings_schema import CHOICE, COLOR, FLAG, FONT, PATH, FieldSpec
from ..theme import tokens
from .buttons import icon_button
from .section import heading_label
from .style_utils import apply_margins, expanding_size_policy


_font_families: list[str] | None = None


def system_font_families() -> list[str]:
    global _font_families
    if _font_families is None:
        try:
            families = QtGui.QFontDatabase.families()
        except TypeError:
            families = QtGui.QFontDatabase().families()
        _font_families = sorted({str(family) for family in families if family}, key=str.lower)
    return list(_font_families)


def read_field(widget: QtWidgets.QWidget):
    if isinstance(widget, QtWidgets.QCheckBox):
        return widget.isChecked()
    if isinstance(widget, QtWidgets.QComboBox):
        return widget.currentText()
    return widget.text()


def write_field(widget: QtWidgets.QWidget, value) -> None:
    if isinstance(widget, QtWidgets.QCheckBox):
        widget.setChecked(bool(value))
    elif isinstance(widget, QtWidgets.QComboBox):
        widget.setCurrentText(str(value or ""))
    else:
        widget.setText(str(value or ""))


def build_field(spec: FieldSpec, value, parent=None) -> QtWidgets.QWidget:
    if spec.kind == FLAG:
        widget = QtWidgets.QCheckBox(parent)
        widget.setChecked(bool(value))
        return widget
    if spec.kind == CHOICE:
        widget = QtWidgets.QComboBox(parent)
        widget.addItems(list(spec.choices))
        widget.setCurrentText(str(value or spec.choices[0]))
    elif spec.kind == FONT:
        widget = QtWidgets.QComboBox(parent)
        widget.addItem("")
        widget.addItems(system_font_families())
        if value and widget.findText(str(value)) < 0:
            widget.addItem(str(value))
        widget.setCurrentText(str(value or ""))
    elif spec.kind == COLOR:
        widget = QtWidgets.QLineEdit(str(value or ""), parent)
        widget.setReadOnly(True)
    else:
        widget = QtWidgets.QLineEdit(str(value if value is not None else ""), parent)
    return expanding_size_policy(widget)


class FormBuilder:
    def __init__(self, parent: QtWidgets.QWidget):
        self.host = parent
        self.layout = QtWidgets.QFormLayout(parent)
        self.layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.fields: dict[str, QtWidgets.QWidget] = {}
        self.rows: dict[str, QtWidgets.QWidget] = {}
        self.labels: dict[str, QtWidgets.QLabel] = {}
        self.buttons: dict[str, QtWidgets.QAbstractButton] = {}

    def add_section(self, title: str) -> QtWidgets.QLabel:
        label = heading_label(title, self.host)
        self.layout.addRow(label)
        return label

    def add_spec(self, spec: FieldSpec, value, on_browse: Callable | None = None, action=None) -> QtWidgets.QWidget:
        field = build_field(spec, value, self.host)
        field.setToolTip(spec.tooltip)
        self.fields[spec.key] = field

        container = QtWidgets.QWidget(self.host)
        row = apply_margins(QtWidgets.QHBoxLayout(container), margins=None, spacing=tokens.SPACE_SM)
        row.addWidget(field, 1)
        if spec.kind == PATH and on_browse is not None:
            button = icon_button("folder", f"Browse for the {spec.label.lower()}", lambda key=spec.key: on_browse(key), container)
            self.buttons[f"browse_{spec.key}"] = button
            row.addWidget(button)
        if action is not None:
            key, icon_name, tooltip, handler = action
            button = icon_button(icon_name, tooltip, handler, container)
            self.buttons[key] = button
            row.addWidget(button)

        label = QtWidgets.QLabel(spec.label, self.host)
        label.setToolTip(spec.tooltip)
        label.setMinimumWidth(tokens.FORM_LABEL_MIN_WIDTH)
        self.labels[spec.key] = label
        self.rows[spec.key] = container
        self.layout.addRow(label, container)
        return field

    def add_widget(self, label: str, widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        self.layout.addRow(label, widget)
        return widget

    def add_row_widget(self, widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        self.layout.addRow(widget)
        return widget

    def set_row_visible(self, key: str, visible: bool) -> None:
        row = self.rows.get(key)
        if row is not None:
            self.layout.setRowVisible(row, visible)

    def is_row_visible(self, key: str) -> bool:
        row = self.rows.get(key)
        return bool(row is not None and self.layout.isRowVisible(row))

    def values(self) -> dict:
        return {key: read_field(widget) for key, widget in self.fields.items()}
