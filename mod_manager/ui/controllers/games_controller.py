from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ...storage import (
    active_game_profile,
    create_game_profile,
    delete_game_profile,
    game_abbreviation,
    load_config,
    save_config,
    set_active_game_profile,
    update_game_profile,
)
from ..dialogs import prompts
from ..dialogs.base import themed_dialog
from ..dialogs.game_profile import GameProfileDialog
from ..pages.toolbar_specs import GAMES_TOOLBAR_SECTIONS
from ..theme import tokens
from ..widgets import IconToolbar, apply_margins, page_title_label
from .widget_registry import ACTIONS

PAGE_TITLE = "Choose game"
DIALOG_TITLE = "Games"
UNKNOWN_ABBREVIATION = "??"
NO_GAME_TOOLTIP = "Choose game"
DELETE_TITLE = "Delete game"
DELETE_QUESTION = "Delete selected game profile?"
ACTIVE_MARK = " *"


class GamesController(QtCore.QObject):
    def __init__(self, window, page: QtWidgets.QWidget):
        super().__init__(window)
        self.window = window
        self.page = page
        self._build_page()
        self._build_dialog()

    @property
    def cfg(self) -> dict:
        return self.window.cfg

    def _toolbar(self, parent, list_widget) -> IconToolbar:
        toolbar = IconToolbar(parent)
        toolbar.build(GAMES_TOOLBAR_SECTIONS)
        toolbar.connect({
            "select": lambda: self.select(self.highlighted_id(list_widget)),
            "add": self.add,
            "edit": lambda: self.edit(self.highlighted_id(list_widget)),
            "delete": lambda: self.delete(self.highlighted_id(list_widget)),
        })
        self.window.registry.extend(ACTIONS, toolbar.buttons.values())
        toolbar.add_stretch()
        return toolbar

    def _list_widget(self) -> QtWidgets.QListWidget:
        widget = QtWidgets.QListWidget()
        widget.itemDoubleClicked.connect(lambda item: self.select(str(item.data(QtCore.Qt.UserRole) or "")))
        return widget

    def _build_page(self) -> None:
        layout = apply_margins(QtWidgets.QVBoxLayout(self.page), margins=tokens.PAGE_MARGIN)
        layout.addWidget(page_title_label(PAGE_TITLE))
        self.page_list = self._list_widget()
        layout.addWidget(self.page_list, 1)
        self.page_toolbar = self._toolbar(self.page, self.page_list)
        layout.addWidget(self.page_toolbar)

    def _build_dialog(self) -> None:
        self.dialog = themed_dialog(self.window, DIALOG_TITLE, tokens.LARGE_DIALOG_SIZE)
        layout = QtWidgets.QVBoxLayout(self.dialog)
        self.dialog_list = self._list_widget()
        layout.addWidget(self.dialog_list, 1)
        self.dialog_toolbar = self._toolbar(self.dialog, self.dialog_list)
        layout.addWidget(self.dialog_toolbar)

    def highlighted_id(self, list_widget: QtWidgets.QListWidget) -> str:
        item = list_widget.currentItem()
        return str(item.data(QtCore.Qt.UserRole) or "") if item else ""

    def update_game_button(self) -> None:
        button = self.window.game_button
        profile = active_game_profile(self.cfg)
        if not profile:
            button.setText(UNKNOWN_ABBREVIATION)
            button.setToolTip(NO_GAME_TOOLTIP)
            return
        button.setText(game_abbreviation(profile.get("name", "")))
        button.setToolTip(f"{profile.get('name', 'Game')} - manage game profiles")

    def refresh_lists(self) -> None:
        profiles = self.cfg.get("game_profiles", []) or []
        active_id = self.cfg.get("active_game_profile_id", "")
        for list_widget in (self.page_list, self.dialog_list):
            list_widget.clear()
            for profile in profiles:
                mark = ACTIVE_MARK if profile.get("id") == active_id else ""
                name = profile.get("name", "Game")
                item = QtWidgets.QListWidgetItem(f"{game_abbreviation(name)}  {name}{mark}")
                item.setData(QtCore.Qt.UserRole, profile.get("id", ""))
                list_widget.addItem(item)
            if list_widget.count():
                list_widget.setCurrentRow(0)
        self.update_game_button()

    def _reload(self) -> dict:
        save_config(self.cfg)
        self.window.cfg = self.window.context.replace_config(load_config())
        self.window.tile_delegate.cfg = self.window.cfg
        self.refresh_lists()
        return self.window.cfg

    def select(self, profile_id: str) -> None:
        if profile_id and set_active_game_profile(self.cfg, profile_id):
            self._reload()
            self.window._set_main_page(self.window.mods_tab)
            self.window.refresh_all()
            self.window._close_dialog(self.dialog)

    def delete(self, profile_id: str) -> None:
        if not profile_id or not prompts.ask_yes_no(self.window, DELETE_TITLE, DELETE_QUESTION):
            return
        if delete_game_profile(self.cfg, profile_id):
            self._reload()
            self.window._show_start_page()
            self.window.refresh_all()

    def add(self) -> None:
        values = GameProfileDialog(self.window).values()
        if not values:
            return
        create_game_profile(values.pop("name"), values, self.cfg)
        self._reload()
        self.window._set_main_page(self.window.mods_tab)
        self.window.refresh_all()

    def edit(self, profile_id: str) -> None:
        profile = next((p for p in self.cfg.get("game_profiles", []) if p.get("id") == profile_id), None)
        if not profile:
            return
        values = GameProfileDialog(self.window, profile).values()
        if not values:
            return
        update_game_profile(self.cfg, profile_id, values)
        self._reload()
        self.window.refresh_all()
