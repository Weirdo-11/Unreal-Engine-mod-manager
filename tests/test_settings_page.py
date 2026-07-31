from __future__ import annotations

import unittest
from unittest.mock import patch

from tests.qt_support import qt_available
from tests.window_fixture import FAKE_DEST, WindowTestCase

from app_paths import DEFAULT_CONFIG

from mod_manager import settings_schema as schema

if qt_available():
    from PySide6 import QtGui, QtWidgets

    from mod_manager.ui.theme import tokens
    from mod_manager.ui.widgets.style_utils import TOOLBAR_SECTION


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class SettingsFormTest(WindowTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_inline_runner()
        self.window._open_settings_dialog()
        self.form = self.window.settings_form

    def test_every_setting_is_rendered_once(self):
        self.assertEqual(set(self.form.fields), {spec.key for spec in schema.all_specs()})

    def test_labels_are_human_readable_not_config_keys(self):
        for spec in schema.all_specs():
            self.assertEqual(self.form.labels[spec.key].text(), spec.label)
            self.assertNotEqual(self.form.labels[spec.key].text(), spec.key)

    def test_every_field_and_label_carries_the_tooltip(self):
        for spec in schema.all_specs():
            self.assertEqual(self.form.fields[spec.key].toolTip(), spec.tooltip, spec.key)
            self.assertEqual(self.form.labels[spec.key].toolTip(), spec.tooltip, spec.key)

    def test_sections_are_rendered_in_schema_order(self):
        self.assertEqual(list(self.form.sections), [title for title, _specs in schema.SETTINGS_SECTIONS])
        for section in self.form.sections.values():
            self.assertEqual(section.property("variant"), TOOLBAR_SECTION)

    def test_compact_fields_use_token_widths(self):
        self.assertEqual(self.form.fields["page_size"].width(), tokens.FORM_SHORT_FIELD_WIDTH)
        self.assertLessEqual(self.form.fields["gui_theme"].maximumWidth(), tokens.FORM_MEDIUM_FIELD_WIDTH)
        self.assertEqual(
            self.form.fields["mods_source_dir"].sizePolicy().horizontalPolicy(),
            QtWidgets.QSizePolicy.Expanding,
        )

    def test_numeric_fields_share_rows_in_pairs(self):
        expected_pairs = (
            ("page_size", "max_mod_name_len"),
            ("max_preset_name_len", "max_label_name_len"),
            ("gui_font_size", "ui_scale_percent"),
            ("tile_size", "placeholder_image_col_width"),
        )
        for first, second in expected_pairs:
            self.assertIs(self.form.rows[first], self.form.rows[second], (first, second))

    def test_compact_fields_align_left_with_other_inputs(self):
        section = self.form.sections["Appearance"]
        theme_x = self.form.fields["gui_theme"].mapTo(section, self.form.fields["gui_theme"].rect().topLeft()).x()
        font_size = self.form.fields["gui_font_size"]
        scale = self.form.fields["ui_scale_percent"]
        font_size_pos = font_size.mapTo(section, font_size.rect().topLeft())
        scale_pos = scale.mapTo(section, scale.rect().topLeft())
        self.assertEqual(font_size_pos.x(), theme_x)
        self.assertEqual(font_size_pos.y(), scale_pos.y())
        self.assertGreater(scale_pos.x(), font_size_pos.x() + font_size.width())

    def test_font_preview_changes_without_changing_application_font(self):
        before = QtWidgets.QApplication.instance().font()
        self.form.fields["gui_font_size"].setText("17")
        font_widget = self.form.fields["gui_font_family"]
        if font_widget.count() > 1:
            font_widget.setCurrentIndex(1)
        self.assertEqual(self.window.settings.font_preview.font().pointSize(), 17)
        self.assertEqual(QtWidgets.QApplication.instance().font(), before)

    def test_per_game_paths_are_visible_settings(self):
        for key in ("mods_source_dir", "game_mods_dir", "mod_extensions", "mod_recursive_scan", "link_prefix"):
            self.assertIn(key, self.form.fields, key)
            self.assertTrue(self.form.is_row_visible(key), key)

    def test_path_settings_get_a_browse_button(self):
        for key in ("mods_source_dir", "game_mods_dir"):
            button = self.form.buttons[f"browse_{key}"]
            self.assertTrue(button.toolTip().startswith("Browse for"), key)

    def test_flag_settings_render_as_checkboxes(self):
        self.assertIsInstance(self.form.fields["mod_recursive_scan"], QtWidgets.QCheckBox)

    def test_choice_settings_render_their_choices(self):
        widget = self.form.fields["gui_theme"]
        self.assertEqual([widget.itemText(i) for i in range(widget.count())], ["system", "light", "dark"])

    def test_browse_writes_the_chosen_path_into_the_field(self):
        with patch("mod_manager.ui.dialogs.prompts.choose_directory", return_value=str(FAKE_DEST)):
            self.window._browse_setting("game_mods_dir")
        self.assertEqual(self.form.fields["game_mods_dir"].text(), str(FAKE_DEST))


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class OlderConfigTest(WindowTestCase):
    """A config.json written by an older version misses newer keys."""

    def setUp(self) -> None:
        super().setUp()
        for key in ("ui_scale_percent", "gui_font_size", "placeholder_image_col_width"):
            self.window.cfg.pop(key, None)
        self.use_inline_runner()
        self.window._open_settings_dialog()

    def test_missing_keys_fall_back_to_the_defaults(self):
        for key in ("ui_scale_percent", "gui_font_size", "placeholder_image_col_width"):
            self.assertEqual(self.window.settings_form.fields[key].text(), str(DEFAULT_CONFIG[key]), key)

    def test_saving_an_older_config_does_not_report_an_error(self):
        with patch("mod_manager.storage.save_config"):
            self.window._save_settings()

        self.assertEqual(self.window.context.status_text, "Settings saved.")
        self.assertEqual(self.window.cfg["ui_scale_percent"], DEFAULT_CONFIG["ui_scale_percent"])


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class SettingsColorTest(WindowTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_inline_runner()
        self.window._open_settings_dialog()
        self.form = self.window.settings_form

    def test_custom_color_rows_are_hidden_in_system_mode(self):
        self.assertFalse(self.form.is_row_visible("gui_accent_color"))
        self.assertFalse(self.form.is_row_visible("gui_text_color"))

    def test_switching_to_custom_reveals_the_color_row(self):
        self.form.fields["gui_accent_color_mode"].setCurrentText("custom")
        self.assertTrue(self.form.is_row_visible("gui_accent_color"))
        self.assertFalse(self.form.is_row_visible("gui_text_color"))

    def test_preview_badge_toggles_the_color_mode(self):
        self.window.accent_preview_badge.click()
        self.assertEqual(self.form.fields["gui_accent_color_mode"].currentText(), "custom")
        self.window.accent_preview_badge.click()
        self.assertEqual(self.form.fields["gui_accent_color_mode"].currentText(), "system")

        self.window.text_preview_badge.click()
        self.assertEqual(self.form.fields["gui_text_color_mode"].currentText(), "custom")

    def test_choosing_a_color_updates_the_field_and_the_preview(self):
        self.form.fields["gui_accent_color_mode"].setCurrentText("custom")
        with patch("mod_manager.ui.dialogs.prompts.choose_color", return_value=QtGui.QColor("#ff0000")):
            self.window._choose_color("gui_accent_color")

        self.assertEqual(self.form.fields["gui_accent_color"].text(), "#ff0000")
        self.assertEqual(self.window._settings_accent_color().name(), "#ff0000")
        self.assertFalse(self.window.accent_preview_badge.icon().isNull())

    def test_cancelling_the_color_dialog_keeps_the_current_value(self):
        self.form.fields["gui_accent_color_mode"].setCurrentText("custom")
        before = self.form.fields["gui_accent_color"].text()
        with patch("mod_manager.ui.dialogs.prompts.choose_color", return_value=QtGui.QColor()):
            self.window._choose_color("gui_accent_color")
        self.assertEqual(self.form.fields["gui_accent_color"].text(), before)


@unittest.skipUnless(qt_available(), "PySide6 is not installed")
class SettingsSaveTest(WindowTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_inline_runner()
        self.window._open_settings_dialog()

    def test_saving_coerces_numeric_fields(self):
        self.window.settings_form.fields["page_size"].setText("25")
        self.window.settings_form.fields["tile_size"].setText("188")

        with patch("mod_manager.storage.save_config"):
            self.window._save_settings()

        self.assertEqual(self.window.cfg["page_size"], 25)
        self.assertEqual(self.window.cfg["tile_size"], 188)
        self.assertEqual(self.window.context.status_text, "Settings saved.")

    def test_saving_an_out_of_range_value_reports_an_error(self):
        self.window.settings_form.fields["page_size"].setText("0")

        with patch("mod_manager.storage.save_config"), patch("mod_manager.ui.dialogs.prompts.show_error") as show_error:
            self.window._save_settings()

        show_error.assert_called_once()
        self.assertIn("Mods per page must be between 1 and 1000.", show_error.call_args[0][2])

    def test_saving_per_game_paths_reaches_the_config(self):
        self.window.settings_form.fields["mod_extensions"].setText(".pak")
        self.window.settings_form.fields["mod_recursive_scan"].setChecked(True)

        with patch("mod_manager.storage.save_config"):
            self.window._save_settings()

        self.assertEqual(self.window.cfg["mod_extensions"], ".pak")
        self.assertIs(self.window.cfg["mod_recursive_scan"], True)

    def test_saving_a_new_state_column_width_resizes_the_column(self):
        self.window.settings_form.fields["placeholder_image_col_width"].setText("96")

        with patch("mod_manager.storage.save_config"):
            self.window._save_settings()

        self.assertEqual(self.window.mods_table.horizontalHeader().sectionSize(0), 96)

    def test_saved_font_applies_to_existing_widgets_without_restart(self):
        self.window.settings_form.fields["gui_font_size"].setText("17")

        with patch("mod_manager.storage.save_config"):
            self.window._save_settings()

        self.assertEqual(QtWidgets.QApplication.instance().font().pointSize(), 17)
        self.assertEqual(self.window.search_box.font().pointSize(), 17)


if __name__ == "__main__":
    unittest.main()
