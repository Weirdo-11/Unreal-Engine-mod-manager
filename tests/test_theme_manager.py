from __future__ import annotations

import os
import unittest

from tests.qt_support import qt_app, qt_available

if qt_available():
    from PySide6 import QtGui

    from mod_manager.ui import apply_ui_scale
    from mod_manager.ui.theme import accent, colors
    from mod_manager.ui.theme.manager import ThemeManager, build_font, custom_accent, custom_text


def base_cfg(**overrides) -> dict:
    cfg = {
        "gui_theme": "system",
        "gui_accent_color_mode": "system",
        "gui_accent_color": "#2563eb",
        "gui_text_color_mode": "system",
        "gui_text_color": "#111827",
        "gui_font_family": "",
        "gui_font_size": 10,
    }
    cfg.update(overrides)
    return cfg


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class ThemeManagerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = qt_app()

    def tearDown(self) -> None:
        self.app.setStyleSheet("")

    def test_apply_resolves_light_and_dark_modes(self):
        for mode in ("light", "dark"):
            manager = ThemeManager(base_cfg(gui_theme=mode))
            palette = manager.apply()
            self.assertEqual(palette.mode, mode)
            self.assertIs(palette.is_dark, mode == "dark")

    def test_apply_installs_the_generated_stylesheet_on_the_application(self):
        manager = ThemeManager(base_cfg(gui_theme="dark"))
        manager.apply()
        self.assertEqual(self.app.styleSheet(), manager.stylesheet)
        self.assertIn(manager.palette.bg, manager.stylesheet)

    def test_apply_emits_changed(self):
        manager = ThemeManager(base_cfg(gui_theme="light"))
        seen = []
        manager.changed.connect(lambda: seen.append(True))
        manager.apply()
        self.assertEqual(len(seen), 1)

    def test_fixed_mode_writes_theme_colors_into_the_qt_palette(self):
        manager = ThemeManager(base_cfg(gui_theme="dark"))
        theme = manager.apply()
        palette = self.app.palette()
        self.assertEqual(palette.color(QtGui.QPalette.Window).name(), theme.bg)
        self.assertEqual(palette.color(QtGui.QPalette.Base).name(), theme.panel)
        self.assertEqual(palette.color(QtGui.QPalette.WindowText).name(), theme.fg)

    def test_custom_accent_overrides_the_system_accent(self):
        manager = ThemeManager(base_cfg(gui_theme="dark", gui_accent_color_mode="custom", gui_accent_color="#ff0000"))
        theme = manager.apply()
        self.assertEqual(theme.accent, "#ff0000")
        self.assertEqual(self.app.palette().color(QtGui.QPalette.Highlight).name(), "#ff0000")

    def test_custom_text_color_overrides_every_text_role(self):
        manager = ThemeManager(base_cfg(gui_theme="dark", gui_text_color_mode="custom", gui_text_color="#00ff00"))
        manager.apply()
        palette = self.app.palette()
        for role in (QtGui.QPalette.WindowText, QtGui.QPalette.Text, QtGui.QPalette.ButtonText, QtGui.QPalette.ToolTipText):
            self.assertEqual(palette.color(role).name(), "#00ff00")

    def test_custom_text_color_reaches_the_stylesheet(self):
        manager = ThemeManager(base_cfg(gui_theme="dark", gui_text_color_mode="custom", gui_text_color="#00ff00"))
        manager.apply()
        self.assertEqual(manager.palette.control_fg, "#00ff00")
        self.assertIn("#00ff00", manager.stylesheet)

    def test_system_color_mode_ignores_the_stored_custom_colors(self):
        cfg = base_cfg(gui_accent_color="#ff0000", gui_text_color="#00ff00")
        self.assertIsNone(custom_accent(cfg))
        self.assertIsNone(custom_text(cfg))

    def test_invalid_custom_colors_are_ignored(self):
        cfg = base_cfg(gui_accent_color_mode="custom", gui_accent_color="nope")
        self.assertIsNone(custom_accent(cfg))

    def test_system_appearance_change_is_ignored_while_applying(self):
        manager = ThemeManager(base_cfg())
        manager._applying = True
        manager._system_palette = QtGui.QPalette()
        manager.on_system_appearance_changed()
        self.assertIsNotNone(manager._system_palette)

    def test_system_appearance_change_drops_the_cached_system_palette(self):
        manager = ThemeManager(base_cfg())
        manager.apply()
        manager.on_system_appearance_changed()
        self.assertIsNotNone(manager.palette)


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class FontTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = qt_app()

    def test_font_size_from_settings_is_applied(self):
        font = build_font(base_cfg(gui_font_size=17), QtGui.QFont())
        self.assertEqual(font.pointSize(), 17)

    def test_font_family_from_settings_is_applied(self):
        font = build_font(base_cfg(gui_font_family="Courier New"), QtGui.QFont())
        self.assertEqual(font.family(), "Courier New")

    def test_empty_font_settings_leave_the_default_font_alone(self):
        self.assertIsNone(build_font(base_cfg(gui_font_family="", gui_font_size=0), QtGui.QFont()))

    def test_invalid_font_size_is_ignored(self):
        font = build_font(base_cfg(gui_font_family="Courier New", gui_font_size="huge"), QtGui.QFont())
        self.assertEqual(font.family(), "Courier New")


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class AccentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = qt_app()

    def test_resolve_mode_passes_through_explicit_modes(self):
        self.assertEqual(accent.resolve_mode("light"), "light")
        self.assertEqual(accent.resolve_mode("dark"), "dark")

    def test_resolve_mode_follows_a_dark_system_palette(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#101010"))
        self.assertEqual(accent.resolve_mode("system", palette), "dark")

    def test_resolve_mode_follows_a_light_system_palette(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#fafafa"))
        self.assertEqual(accent.resolve_mode("system", palette), "light")

    def test_system_accent_reads_the_highlight_role(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#123456"))
        self.assertEqual(accent.system_accent(palette), "#123456")

    def test_system_accent_falls_back_to_a_valid_color(self):
        self.assertIsNotNone(colors.normalize_hex(accent.system_accent()))


class UiScaleTest(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = os.environ.pop("QT_SCALE_FACTOR", None)

    def tearDown(self) -> None:
        os.environ.pop("QT_SCALE_FACTOR", None)
        if self._saved is not None:
            os.environ["QT_SCALE_FACTOR"] = self._saved

    @unittest.skipUnless(qt_available(), "PySide6 is not installed")
    def test_scale_is_exported_for_qt(self):
        apply_ui_scale({"ui_scale_percent": 150})
        self.assertEqual(os.environ["QT_SCALE_FACTOR"], "1.5")

    @unittest.skipUnless(qt_available(), "PySide6 is not installed")
    def test_default_scale_is_not_exported(self):
        apply_ui_scale({"ui_scale_percent": 100})
        self.assertNotIn("QT_SCALE_FACTOR", os.environ)

    @unittest.skipUnless(qt_available(), "PySide6 is not installed")
    def test_invalid_scale_is_ignored(self):
        apply_ui_scale({"ui_scale_percent": "big"})
        self.assertNotIn("QT_SCALE_FACTOR", os.environ)


if __name__ == "__main__":
    unittest.main()
