from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ... import settings_schema
from ...settings_schema import SETTINGS_SECTIONS
from ...workers import _run_save_settings
from .. import icons
from ..dialogs import prompts
from ..dialogs.base import themed_dialog
from ..pages.toolbar_specs import SETTINGS_TOOLBAR_SECTIONS
from ..theme import colors, tokens
from ..widgets import FormBuilder, IconToolbar, apply_margins
from .widget_registry import ACTIONS

TITLE = "Settings"
SAVED_MESSAGE = "Settings saved."
PREVIEW_LABEL = "Theme preview"
ACCENT_KEY = "gui_accent_color"
TEXT_KEY = "gui_text_color"
MODE_SUFFIX = "_mode"

COLOR_ACTIONS = {
    ACCENT_KEY: ("choose_accent", "image", "Choose the accent colour"),
    TEXT_KEY: ("choose_text", "image", "Choose the text colour"),
}

THEME_KEYS = (
    "gui_theme",
    "gui_accent_color_mode",
    ACCENT_KEY,
    "gui_text_color_mode",
    TEXT_KEY,
    "gui_font_family",
    "gui_font_size",
)


class SettingsController(QtCore.QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.dialog = themed_dialog(window, TITLE, tokens.LARGE_DIALOG_SIZE)
        self._build()

    @property
    def cfg(self) -> dict:
        return self.window.cfg

    @property
    def fields(self) -> dict:
        return self.form.fields

    def _build(self) -> None:
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        wrapper = QtWidgets.QWidget()
        wrapper_layout = QtWidgets.QVBoxLayout(wrapper)
        wrapper_layout.setAlignment(QtCore.Qt.AlignTop)
        host = QtWidgets.QWidget()
        self.form = FormBuilder(host)

        values = settings_schema.read_settings(self.cfg)
        for title, specs in SETTINGS_SECTIONS:
            self.form.add_section(title)
            for spec in specs:
                action = None
                if spec.key in COLOR_ACTIONS:
                    key, icon_name, tooltip = COLOR_ACTIONS[spec.key]
                    action = (key, icon_name, tooltip, lambda k=spec.key: self.choose_color(k))
                self.form.add_spec(spec, values[spec.key], self.browse, action)

        self.form.add_widget(PREVIEW_LABEL, self._build_preview_row())
        for key in (ACCENT_KEY, TEXT_KEY):
            self.fields[key + MODE_SUFFIX].currentTextChanged.connect(self._on_color_mode_changed)
        self.update_color_rows()
        self.update_preview()

        self.toolbar = IconToolbar(self.dialog)
        self.toolbar.build(SETTINGS_TOOLBAR_SECTIONS)
        self.toolbar.connect({"save_settings": self.save})
        self.window.registry.extend(ACTIONS, self.toolbar.buttons.values())
        self.toolbar.add_stretch()

        wrapper_layout.addWidget(host)
        wrapper_layout.addStretch(1)
        scroll.setWidget(wrapper)
        layout = QtWidgets.QVBoxLayout(self.dialog)
        layout.addWidget(scroll)
        layout.addWidget(self.toolbar)

    def _preview_badge(self, tooltip: str, handler, text: str = "") -> QtWidgets.QToolButton:
        badge = QtWidgets.QToolButton()
        badge.setText(text)
        badge.setAutoRaise(True)
        badge.setIconSize(QtCore.QSize(tokens.PREVIEW_ICON_SIZE, tokens.PREVIEW_ICON_SIZE))
        badge.setCursor(QtCore.Qt.PointingHandCursor)
        badge.setToolTip(tooltip)
        badge.clicked.connect(handler)
        return badge

    def _build_preview_row(self) -> QtWidgets.QWidget:
        self.accent_badge = self._preview_badge("Click to toggle accent color mode", lambda: self.toggle_color_mode(ACCENT_KEY))
        self.accent_button = QtWidgets.QPushButton("Active")
        self.accent_button.setEnabled(False)
        self.text_badge = self._preview_badge("Click to toggle text color mode", lambda: self.toggle_color_mode(TEXT_KEY), "Aa")
        container = QtWidgets.QWidget()
        row = apply_margins(QtWidgets.QHBoxLayout(container), margins=None)
        row.addWidget(self.accent_badge)
        row.addWidget(self.accent_button)
        row.addWidget(self.text_badge)
        row.addStretch(1)
        return container

    def browse(self, key: str) -> None:
        path = prompts.choose_directory(self.window, settings_schema.label_for(key))
        if path:
            widget = self.fields.get(key)
            if isinstance(widget, QtWidgets.QLineEdit):
                widget.setText(path)

    def fallback_color(self, key: str) -> QtGui.QColor:
        palette = self.window.theme.palette
        return QtGui.QColor(palette.accent if key == ACCENT_KEY else palette.fg)

    def color(self, key: str) -> QtGui.QColor:
        if self.fields[key + MODE_SUFFIX].currentText() == "custom":
            value = QtGui.QColor(self.fields[key].text())
            if value.isValid():
                return value
        return self.fallback_color(key)

    def choose_color(self, key: str) -> None:
        current = QtGui.QColor(self.fields[key].text())
        if not current.isValid():
            current = self.fallback_color(key)
        chosen = prompts.choose_color(self.dialog, current, f"Choose {settings_schema.label_for(key).lower()}")
        if chosen.isValid():
            self.fields[key].setText(chosen.name())
            self.update_preview()

    def toggle_color_mode(self, key: str) -> None:
        combo = self.fields[key + MODE_SUFFIX]
        combo.setCurrentText("custom" if combo.currentText() == "system" else "system")

    def update_color_rows(self) -> None:
        for spec in settings_schema.all_specs():
            if spec.depends_on:
                other_key, required = spec.depends_on
                self.form.set_row_visible(spec.key, self.fields[other_key].currentText() == required)

    def _on_color_mode_changed(self, _text: str = "") -> None:
        self.update_color_rows()
        self.update_preview()

    def update_preview(self) -> None:
        accent = self.color(ACCENT_KEY)
        text = self.color(TEXT_KEY)
        preview = colors.build_palette(self.window.theme.palette.mode, accent.name(), text.name())
        pad_v, pad_h = tokens.BUTTON_PADDING
        self.accent_badge.setIcon(icons.check_icon(accent, size=tokens.PREVIEW_ICON_SIZE))
        self.accent_button.setStyleSheet(
            f"background-color: {preview.accent_fill};"
            f"border: {tokens.BORDER_WIDTH}px solid {preview.accent_border};"
            f"border-radius: {tokens.RADIUS_LG}px;"
            f"padding: {pad_v}px {pad_h}px; color: {preview.fg};"
        )
        self.text_badge.setStyleSheet(f"color: {preview.fg}; font-weight: 600;")

    def theme_settings(self, cfg: dict | None = None) -> tuple:
        source = self.cfg if cfg is None else cfg
        return tuple(str(source.get(key, "") or "") for key in THEME_KEYS)

    def save(self) -> None:
        old_theme = self.theme_settings()
        values = self.form.values()
        try:
            settings_schema.coerce_settings(values)
        except ValueError as error:
            prompts.show_error(self.dialog, TITLE, str(error))
            return

        def done(new_cfg):
            self.window.apply_saved_settings(new_cfg, old_theme != self.theme_settings(new_cfg))

        self.window._run_action("Saving settings...", lambda: _run_save_settings(self.cfg, values), done)
