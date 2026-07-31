from __future__ import annotations

import unittest

from mod_manager.ui.theme import colors, tokens

LEGACY_DARK = {
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
}

LEGACY_LIGHT = {
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
}

LEGACY_BUTTON_OVERLAYS = {
    "dark": {
        "button_normal": "rgba(255, 255, 255, 22)",
        "button_hover": "rgba(255, 255, 255, 38)",
        "button_pressed": "rgba(255, 255, 255, 55)",
        "button_disabled": "rgba(255, 255, 255, 10)",
    },
    "light": {
        "button_normal": "rgba(0, 0, 0, 35)",
        "button_hover": "rgba(0, 0, 0, 55)",
        "button_pressed": "rgba(0, 0, 0, 75)",
        "button_disabled": "rgba(0, 0, 0, 15)",
    },
}

LEGACY_TILE_DARK = {
    "tile_base": (30, 41, 59, 188),
    "tile_base_selected": (30, 64, 175, 170),
    "tile_border": (148, 163, 184, 112),
    "tile_border_selected": (96, 165, 250, 205),
    "tile_shine": (255, 255, 255, 42),
    "tile_end": (15, 23, 42, 148),
    "tile_shadow": (0, 0, 0, 72),
    "tile_inner": (255, 255, 255, 68),
    "placeholder_bg": (30, 41, 59, 155),
}

LEGACY_TILE_LIGHT = {
    "tile_base": (255, 255, 255, 172),
    "tile_base_selected": (219, 234, 254, 188),
    "tile_border": (148, 163, 184, 150),
    "tile_border_selected": (59, 130, 246, 210),
    "tile_shine": (255, 255, 255, 214),
    "tile_end": (226, 232, 240, 132),
    "tile_shadow": (15, 23, 42, 24),
    "tile_inner": (255, 255, 255, 165),
    "placeholder_bg": (226, 232, 240, 150),
}


class PaletteParityTest(unittest.TestCase):
    def test_dark_surface_colors_match_the_previous_theme(self):
        palette = colors.build_palette("dark", colors.FALLBACK_ACCENT)
        for name, expected in LEGACY_DARK.items():
            self.assertEqual(getattr(palette, name), expected, name)

    def test_light_surface_colors_match_the_previous_theme(self):
        palette = colors.build_palette("light", colors.FALLBACK_ACCENT)
        for name, expected in LEGACY_LIGHT.items():
            self.assertEqual(getattr(palette, name), expected, name)

    def test_button_overlays_match_the_previous_theme(self):
        for mode, expected in LEGACY_BUTTON_OVERLAYS.items():
            palette = colors.build_palette(mode, colors.FALLBACK_ACCENT)
            for name, value in expected.items():
                self.assertEqual(getattr(palette, name), value, f"{mode}.{name}")

    def test_tile_colors_match_the_previous_theme(self):
        for mode, expected in (("dark", LEGACY_TILE_DARK), ("light", LEGACY_TILE_LIGHT)):
            palette = colors.build_palette(mode, colors.FALLBACK_ACCENT)
            for name, (red, green, blue, alpha) in expected.items():
                value = getattr(palette, name)
                self.assertEqual(colors.hex_to_rgb(value.color), (red, green, blue), f"{mode}.{name}")
                self.assertEqual(value.alpha, alpha, f"{mode}.{name}")

    def test_placeholder_text_and_state_colors_match_the_previous_theme(self):
        dark = colors.build_palette("dark")
        light = colors.build_palette("light")
        self.assertEqual(dark.placeholder_fg, "#cbd5e1")
        self.assertEqual(light.placeholder_fg, "#64748b")
        self.assertEqual(dark.state_ok, "#16a34a")
        self.assertEqual(dark.state_bad, "#dc2626")

    def test_accent_colors_are_derived_from_the_accent(self):
        palette = colors.build_palette("dark", "#2563eb")
        self.assertEqual(palette.accent, "#2563eb")
        self.assertEqual(palette.accent_text, "#ffffff")
        self.assertEqual(palette.accent_fill, "rgba(37, 99, 235, 84)")
        self.assertEqual(palette.accent_border, "rgba(37, 99, 235, 150)")

    def test_a_bright_accent_gets_dark_readable_text(self):
        palette = colors.build_palette("light", "#fefefe")
        self.assertEqual(palette.accent_text, "#000000")

    def test_an_invalid_accent_falls_back(self):
        for value in ("", None, "not-a-color", "#12345"):
            self.assertEqual(colors.build_palette("dark", value).accent, colors.FALLBACK_ACCENT)

    def test_light_and_dark_define_exactly_the_same_keys(self):
        self.assertEqual(set(colors.LIGHT_BASE), set(colors.DARK_BASE))
        self.assertEqual(set(colors.LIGHT_TRANSLUCENT), set(colors.DARK_TRANSLUCENT))

    def test_unknown_mode_resolves_to_light(self):
        self.assertEqual(colors.build_palette("system").mode, "light")
        self.assertFalse(colors.build_palette("system").is_dark)
        self.assertTrue(colors.build_palette("dark").is_dark)


class TextOverrideTest(unittest.TestCase):
    def test_custom_text_color_replaces_every_text_role(self):
        palette = colors.build_palette("dark", colors.FALLBACK_ACCENT, "#ff0000")
        for name in colors.TEXT_OVERRIDE_FIELDS:
            self.assertEqual(getattr(palette, name), "#ff0000", name)

    def test_custom_text_color_leaves_surfaces_untouched(self):
        palette = colors.build_palette("dark", colors.FALLBACK_ACCENT, "#ff0000")
        self.assertEqual(palette.bg, LEGACY_DARK["bg"])
        self.assertEqual(palette.panel, LEGACY_DARK["panel"])

    def test_invalid_text_override_is_ignored(self):
        palette = colors.build_palette("dark", colors.FALLBACK_ACCENT, "nonsense")
        self.assertEqual(palette.fg, LEGACY_DARK["fg"])


class ColorMathTest(unittest.TestCase):
    def test_normalize_hex_accepts_short_and_long_forms(self):
        self.assertEqual(colors.normalize_hex("#ABC"), "#aabbcc")
        self.assertEqual(colors.normalize_hex("  #A1B2C3 "), "#a1b2c3")
        self.assertIsNone(colors.normalize_hex("a1b2c3"))
        self.assertIsNone(colors.normalize_hex("#zzzzzz"))

    def test_hex_and_rgb_round_trip(self):
        self.assertEqual(colors.hex_to_rgb("#1e293b"), (30, 41, 59))
        self.assertEqual(colors.rgb_to_hex(30, 41, 59), "#1e293b")

    def test_rgb_to_hex_clamps_out_of_range_values(self):
        self.assertEqual(colors.rgb_to_hex(-5, 300, 128), "#00ff80")

    def test_blend_interpolates_between_two_colors(self):
        self.assertEqual(colors.blend("#000000", "#ffffff", 0.0), "#ffffff")
        self.assertEqual(colors.blend("#000000", "#ffffff", 1.0), "#000000")
        self.assertEqual(colors.blend("#000000", "#ffffff", 0.5), "#808080")

    def test_readable_on_picks_a_contrasting_text_color(self):
        self.assertEqual(colors.readable_on("#ffffff"), "#000000")
        self.assertEqual(colors.readable_on("#000000"), "#ffffff")

    def test_is_dark_color_matches_the_luminance_threshold(self):
        self.assertTrue(colors.is_dark_color("#202124"))
        self.assertFalse(colors.is_dark_color("#f8fafc"))

    def test_mode_normalizers_reject_unknown_values(self):
        self.assertEqual(colors.normalize_mode("DARK"), "dark")
        self.assertEqual(colors.normalize_mode("nope"), "system")
        self.assertEqual(colors.normalize_color_mode("Custom"), "custom")
        self.assertEqual(colors.normalize_color_mode(None), "system")


class TokenTest(unittest.TestCase):
    def test_column_specs_are_well_formed(self):
        specs = (tokens.MOD_COLUMNS, tokens.PRESET_COLUMNS, tokens.BROKEN_COLUMNS)
        resize_modes = {tokens.RESIZE_FIXED, tokens.RESIZE_STRETCH, tokens.RESIZE_CONTENTS}
        alignments = {tokens.ALIGN_LEFT, tokens.ALIGN_CENTER, tokens.ALIGN_RIGHT}
        for columns in specs:
            self.assertTrue(columns)
            for key, title, resize, align in columns:
                self.assertTrue(key)
                self.assertIsInstance(title, str)
                self.assertIn(resize, resize_modes)
                self.assertIn(align, alignments)

    def test_clamp_tile_size_stays_within_bounds(self):
        self.assertEqual(tokens.clamp_tile_size(10), tokens.TILE_SIZE_MIN)
        self.assertEqual(tokens.clamp_tile_size(9999), tokens.TILE_SIZE_MAX)
        self.assertEqual(tokens.clamp_tile_size(140), 140)
        self.assertEqual(tokens.clamp_tile_size(None), tokens.TILE_SIZE_MIN)
        self.assertEqual(tokens.clamp_tile_size("junk"), tokens.TILE_SIZE_MIN)

    def test_tile_item_size_adds_the_card_padding(self):
        self.assertEqual(tokens.tile_item_size(140), (140 + tokens.TILE_EXTRA_WIDTH, 140 + tokens.TILE_EXTRA_HEIGHT))

    def test_scaled_clamps_the_percentage(self):
        self.assertEqual(tokens.scaled(100, 100), 100)
        self.assertEqual(tokens.scaled(100, 200), 200)
        self.assertEqual(tokens.scaled(100, 10), tokens.SCALE_MIN)
        self.assertEqual(tokens.scaled(100, "junk"), 100)


if __name__ == "__main__":
    unittest.main()
