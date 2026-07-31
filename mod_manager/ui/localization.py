from __future__ import annotations

import locale

TRANSLATIONS = {
    "install": {"uk": "Встановити", "ru": "Установить", "de": "Installieren", "fr": "Installer", "pl": "Zainstaluj", "it": "Installa", "es": "Instalar"},
    "uninstall": {"uk": "Видалити", "ru": "Удалить", "de": "Deinstallieren", "fr": "Désinstaller", "pl": "Odinstaluj", "it": "Disinstalla", "es": "Desinstalar"},
}


def system_language() -> str:
    try:
        return (locale.getdefaultlocale()[0] or "en").split("_")[0].lower()
    except Exception:
        return "en"


def system_action_text(key: str) -> str:
    return TRANSLATIONS.get(key, {}).get(system_language(), key.capitalize())
