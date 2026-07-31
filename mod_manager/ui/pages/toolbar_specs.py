from __future__ import annotations

MODS_TOOLBAR_SECTIONS = (
    ("game", "Game", ()),
    ("filter", "Search", (
        ("search", "search", "Apply search and label filters"),
        ("clear", "clear", "Clear search and label filters"),
    )),
    ("order", "Order", ()),
    ("view", "View", (
        ("view_list", "list", "Show mods as a list"),
        ("view_tiles", "image", "Show mods as tiles"),
    )),
    ("manage", "Manage", (
        ("presets", "save", "Open presets"),
        ("settings", "open", "Open settings"),
        ("broken", "delete", "Open broken links cleanup"),
    )),
)

MODS_ACTION_SECTIONS = (
    ("page", "Page", ()),
    ("state", "Install", (
        ("install_page", "install", "Install all mods on the current page"),
        ("uninstall_page", "uninstall", "Uninstall all mods on the current page"),
        ("toggle_selected", "toggle", "Toggle selected mods"),
    )),
    ("label", "Label", (
        ("add_label", "add", "Add label to selected mods"),
        ("remove_label", "remove", "Remove label from selected mods"),
    )),
    ("import", "Import", (
        ("import_files", "import", "Import mod files"),
        ("import_folder", "folder", "Import a mod folder"),
        ("set_image", "image", "Set preview image for the selected mod"),
    )),
)

PRESETS_TOOLBAR_SECTIONS = (
    ("page", "Page", ()),
    ("preset", "Presets", (
        ("save", "save", "Save the installed mods as a preset"),
        ("toggle", "toggle", "Toggle selected presets"),
        ("delete", "delete", "Delete selected presets"),
    )),
)

BROKEN_TOOLBAR_SECTIONS = (
    ("cleanup", "Broken links", (
        ("remove_selected", "remove", "Remove selected broken links"),
        ("remove_all", "delete", "Remove all broken links"),
    )),
)

GAMES_TOOLBAR_SECTIONS = (
    ("choose", "Game", (
        ("select", "toggle", "Select the highlighted game"),
    )),
    ("profiles", "Profiles", (
        ("add", "add", "Add a game profile"),
        ("edit", "open", "Edit the highlighted game profile"),
        ("delete", "delete", "Delete the highlighted game profile"),
    )),
)

SETTINGS_TOOLBAR_SECTIONS = (
    ("settings", "Settings", (
        ("save_settings", "save", "Save settings"),
    )),
)

SELECTION_ACTIONS = ("toggle_selected", "add_label", "remove_label", "set_image")


def section_keys(specs) -> tuple[str, ...]:
    return tuple(key for key, _title, _actions in specs)


def button_keys(specs) -> tuple[str, ...]:
    return tuple(key for _section, _title, actions in specs for key, _icon, _tooltip in actions)
