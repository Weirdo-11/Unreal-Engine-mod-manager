from __future__ import annotations

from dataclasses import dataclass

THEME_MODES = ("system", "light", "dark")
COLOR_MODES = ("system", "custom")

FALLBACK_ACCENT = "#2563eb"
FALLBACK_TEXT = "#111827"
STATE_OK = "#16a34a"
STATE_BAD = "#dc2626"

DARK_THRESHOLD = 0.45
READABLE_THRESHOLD = 0.58

LIGHT_BASE = {
    "bg": "#f8fafc",
    "fg": "#111827",
    "control_fg": "#111827",
    "panel": "#ffffff",
    "alt_panel": "#eef2f7",
    "button": "#f1f5f9",
    "tooltip_bg": "#ffffff",
    "tooltip_fg": "#111827",
    "field": "#f4f4f5",
    "field_border": "#d4d4d8",
    "field_focus": "#9291a5",
    "field_fg": "#111827",
    "combo": "#e4e4e7",
    "combo_hover": "#d4d4d8",
    "combo_focus": "#c4c4ca",
    "combo_list": "#ffffff",
    "combo_list_border": "#d4d4d8",
    "menu": "#ffffff",
    "menu_border": "#d4d4d8",
    "menu_selected": "#e4e4e7",
    "border": "#d4d4d8",
    "muted": "#64748b",
    "placeholder_fg": "#64748b",
}

DARK_BASE = {
    "bg": "#202124",
    "fg": "#f8fafc",
    "control_fg": "#f2f2f5",
    "panel": "#111827",
    "alt_panel": "#1f2937",
    "button": "#2b2f36",
    "tooltip_bg": "#111827",
    "tooltip_fg": "#f8fafc",
    "field": "#2d2d30",
    "field_border": "#3f3f42",
    "field_focus": "#6b6a7c",
    "field_fg": "#f2f2f5",
    "combo": "#626071",
    "combo_hover": "#716f82",
    "combo_focus": "#78758a",
    "combo_list": "#2d2d30",
    "combo_list_border": "#56565c",
    "menu": "#2d2d30",
    "menu_border": "#3f3f42",
    "menu_selected": "#626071",
    "border": "#3f3f42",
    "muted": "#94a3b8",
    "placeholder_fg": "#cbd5e1",
}

LIGHT_TRANSLUCENT = {
    "placeholder_bg": ("#e2e8f0", 150),
    "tile_base": ("#ffffff", 172),
    "tile_base_selected": ("#dbeafe", 188),
    "tile_border": ("#94a3b8", 150),
    "tile_border_selected": ("#3b82f6", 210),
    "tile_shine": ("#ffffff", 214),
    "tile_end": ("#e2e8f0", 132),
    "tile_shadow": ("#0f172a", 24),
    "tile_inner": ("#ffffff", 165),
}

DARK_TRANSLUCENT = {
    "placeholder_bg": ("#1e293b", 155),
    "tile_base": ("#1e293b", 188),
    "tile_base_selected": ("#1e40af", 170),
    "tile_border": ("#94a3b8", 112),
    "tile_border_selected": ("#60a5fa", 205),
    "tile_shine": ("#ffffff", 42),
    "tile_end": ("#0f172a", 148),
    "tile_shadow": ("#000000", 72),
    "tile_inner": ("#ffffff", 68),
}

BUTTON_OVERLAY = {
    "light": ("#000000", {"normal": 35, "hover": 55, "pressed": 75, "disabled": 15}),
    "dark": ("#ffffff", {"normal": 22, "hover": 38, "pressed": 55, "disabled": 10}),
}

ACCENT_FILL_ALPHA = 84
ACCENT_BORDER_ALPHA = 150

TEXT_OVERRIDE_FIELDS = ("fg", "control_fg", "field_fg", "tooltip_fg")


def normalize_hex(value) -> str | None:
    text = str(value or "").strip()
    if not text.startswith("#"):
        return None
    digits = text[1:]
    if len(digits) == 3:
        digits = "".join(char * 2 for char in digits)
    if len(digits) != 6:
        return None
    try:
        int(digits, 16)
    except ValueError:
        return None
    return "#" + digits.lower()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    digits = (normalize_hex(value) or FALLBACK_ACCENT)[1:]
    return int(digits[0:2], 16), int(digits[2:4], 16), int(digits[4:6], 16)


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    clamped = tuple(max(0, min(255, int(round(part)))) for part in (red, green, blue))
    return "#%02x%02x%02x" % clamped


def rgba_css(value: str, alpha: int) -> str:
    red, green, blue = hex_to_rgb(value)
    return f"rgba({red}, {green}, {blue}, {int(alpha)})"


def blend(first: str, second: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, float(ratio)))
    one = hex_to_rgb(first)
    two = hex_to_rgb(second)
    return rgb_to_hex(*(one[i] * ratio + two[i] * (1.0 - ratio) for i in range(3)))


def luminance(value: str) -> float:
    red, green, blue = (part / 255.0 for part in hex_to_rgb(value))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def is_dark_color(value: str) -> bool:
    return luminance(value) < DARK_THRESHOLD


def readable_on(value: str) -> str:
    return "#000000" if luminance(value) > READABLE_THRESHOLD else "#ffffff"


def normalize_mode(value) -> str:
    mode = str(value or "system").strip().lower()
    return mode if mode in THEME_MODES else "system"


def normalize_color_mode(value) -> str:
    mode = str(value or "system").strip().lower()
    return mode if mode in COLOR_MODES else "system"


@dataclass(frozen=True)
class Rgba:
    color: str
    alpha: int

    @property
    def css(self) -> str:
        return rgba_css(self.color, self.alpha)


@dataclass(frozen=True)
class Palette:
    mode: str
    bg: str
    fg: str
    control_fg: str
    panel: str
    alt_panel: str
    button: str
    tooltip_bg: str
    tooltip_fg: str
    field: str
    field_border: str
    field_focus: str
    field_fg: str
    combo: str
    combo_hover: str
    combo_focus: str
    combo_list: str
    combo_list_border: str
    menu: str
    menu_border: str
    menu_selected: str
    border: str
    muted: str
    placeholder_fg: str
    accent: str
    accent_text: str
    accent_fill: str
    accent_border: str
    button_normal: str
    button_hover: str
    button_pressed: str
    button_disabled: str
    state_ok: str
    state_bad: str
    placeholder_bg: Rgba
    tile_base: Rgba
    tile_base_selected: Rgba
    tile_border: Rgba
    tile_border_selected: Rgba
    tile_shine: Rgba
    tile_end: Rgba
    tile_shadow: Rgba
    tile_inner: Rgba

    @property
    def is_dark(self) -> bool:
        return self.mode == "dark"


def build_palette(mode: str, accent: str | None = None, text: str | None = None) -> Palette:
    resolved_mode = "dark" if str(mode).lower() == "dark" else "light"
    base = dict(DARK_BASE if resolved_mode == "dark" else LIGHT_BASE)
    translucent = DARK_TRANSLUCENT if resolved_mode == "dark" else LIGHT_TRANSLUCENT

    text_override = normalize_hex(text)
    if text_override:
        for field in TEXT_OVERRIDE_FIELDS:
            base[field] = text_override

    accent_color = normalize_hex(accent) or FALLBACK_ACCENT
    overlay_color, alphas = BUTTON_OVERLAY[resolved_mode]

    return Palette(
        mode=resolved_mode,
        accent=accent_color,
        accent_text=readable_on(accent_color),
        accent_fill=rgba_css(accent_color, ACCENT_FILL_ALPHA),
        accent_border=rgba_css(accent_color, ACCENT_BORDER_ALPHA),
        button_normal=rgba_css(overlay_color, alphas["normal"]),
        button_hover=rgba_css(overlay_color, alphas["hover"]),
        button_pressed=rgba_css(overlay_color, alphas["pressed"]),
        button_disabled=rgba_css(overlay_color, alphas["disabled"]),
        state_ok=STATE_OK,
        state_bad=STATE_BAD,
        **base,
        **{key: Rgba(*value) for key, value in translucent.items()},
    )
