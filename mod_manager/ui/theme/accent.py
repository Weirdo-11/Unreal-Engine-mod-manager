from __future__ import annotations

from PySide6 import QtGui, QtWidgets

from .colors import FALLBACK_ACCENT, is_dark_color, normalize_mode, rgb_to_hex

WINDOWS_DWM_KEY = r"Software\Microsoft\Windows\DWM"
WINDOWS_PERSONALIZE_KEY = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"


def _read_registry_dword(sub_key: str, value_name: str):
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            value, _kind = winreg.QueryValueEx(key, value_name)
    except OSError:
        return None
    return value if isinstance(value, int) else None


def windows_accent() -> str | None:
    value = _read_registry_dword(WINDOWS_DWM_KEY, "AccentColor")
    if value is None:
        return None
    return rgb_to_hex(value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF)


def windows_prefers_dark() -> bool | None:
    value = _read_registry_dword(WINDOWS_PERSONALIZE_KEY, "AppsUseLightTheme")
    return None if value is None else value == 0


def palette_color(role, palette: QtGui.QPalette | None = None) -> str | None:
    if palette is None:
        app = QtWidgets.QApplication.instance()
        if app is None:
            return None
        palette = app.palette()
    color = palette.color(role)
    return color.name() if color.isValid() else None


def system_accent(palette: QtGui.QPalette | None = None) -> str:
    return palette_color(QtGui.QPalette.Highlight, palette) or windows_accent() or FALLBACK_ACCENT


def system_prefers_dark(palette: QtGui.QPalette | None = None) -> bool:
    window = palette_color(QtGui.QPalette.Window, palette)
    if window is not None:
        return is_dark_color(window)
    prefers_dark = windows_prefers_dark()
    return bool(prefers_dark)


def resolve_mode(configured, palette: QtGui.QPalette | None = None) -> str:
    mode = normalize_mode(configured)
    if mode != "system":
        return mode
    return "dark" if system_prefers_dark(palette) else "light"
