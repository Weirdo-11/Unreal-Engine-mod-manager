from __future__ import annotations

LIST = "list"
TILES = "tiles"
VIEW_MODES = (LIST, TILES)

MOD_ORDER_OPTIONS = {
    "Default": "default",
    "Created date": "created_date",
    "Last managed": "last_managed",
    "Label": "label",
    "Name": "name",
    "Installed": "installed",
}

MOD_ORDER_ALIASES = {
    "d": "default",
    "Default": "default",
    "Default (name without prefix)": "default",
    "Created date": "created_date",
    "cd": "created_date",
    "created date": "created_date",
}

MOD_COLUMN_SORT_KEYS = ("installed", "name", "label", "last_managed")

DEFAULT_ORDER_LABEL = "Default"
DEFAULT_ORDER_KEY = "default"


def normalize_view_mode(value) -> str:
    mode = str(value or LIST).strip().lower()
    return mode if mode in VIEW_MODES else LIST


def normalize_sort_key(key) -> str:
    key = MOD_ORDER_ALIASES.get(key, key)
    return key if key in set(MOD_ORDER_OPTIONS.values()) else DEFAULT_ORDER_KEY


def order_label_for_key(key) -> str:
    key = normalize_sort_key(key)
    for label, value in MOD_ORDER_OPTIONS.items():
        if value == key:
            return label
    return DEFAULT_ORDER_LABEL


def order_label_from_config(cfg: dict) -> str:
    key = normalize_sort_key(cfg.get("mod_sort_key", DEFAULT_ORDER_KEY))
    if key == DEFAULT_ORDER_KEY:
        key = normalize_sort_key(cfg.get("order_var", DEFAULT_ORDER_KEY))
    return order_label_for_key(key)


def sort_key_for_column(section: int) -> str:
    if 0 <= section < len(MOD_COLUMN_SORT_KEYS):
        return MOD_COLUMN_SORT_KEYS[section]
    return ""


def order_mode(key: str, reverse: bool) -> str:
    key = normalize_sort_key(key)
    return f"-{key}" if reverse else key
