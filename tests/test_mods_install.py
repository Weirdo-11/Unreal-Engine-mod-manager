from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mod_manager.mods import (
    apply_mods_batch,
    deactivate_mod,
    discover_mods,
    existing_targets,
    overwrite_message,
)

GROUP_SUFFIXES = (".pak", ".utoc", ".ucas")


class CopyInstallTests(unittest.TestCase):
    """Copy installs touch the real filesystem; unlike mklink they need no admin rights."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name) / "source"
        self.dst = Path(self.tmp.name) / "game"
        self.src.mkdir()
        self.dst.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _cfg(self, **overrides) -> dict:
        cfg = {
            "mods_source_dir": str(self.src),
            "game_mods_dir": str(self.dst),
            "mod_extensions": ".pak,.utoc,.ucas",
            "mod_group_extensions": "",
            "mod_recursive_scan": False,
            "link_prefix": "",
            "install_mode": "copy",
        }
        cfg.update(overrides)
        return cfg

    def _write(self, name: str, text: str = "mod") -> Path:
        path = self.src / name
        path.write_text(text, encoding="utf-8")
        return path

    def _write_group(self, stem: str, text: str = "mod") -> None:
        for suffix in GROUP_SUFFIXES:
            self._write(f"{stem}{suffix}", text)

    def _mods(self, **overrides):
        return discover_mods(self._cfg(**overrides))

    def test_installing_copies_the_file_and_keeps_the_source(self):
        self._write("Weapon.pak", "payload")

        results = apply_mods_batch(self._mods())

        self.assertEqual(results, [(True, "OK")])
        self.assertEqual((self.dst / "Weapon.pak").read_text(encoding="utf-8"), "payload")
        self.assertTrue((self.src / "Weapon.pak").exists())

    def test_installing_a_folder_copies_its_contents(self):
        folder = self.src / "FolderMod"
        (folder / "inner").mkdir(parents=True)
        (folder / "inner" / "data.bin").write_text("data", encoding="utf-8")

        results = apply_mods_batch(self._mods(mod_extensions="folders"))

        self.assertEqual(results, [(True, "OK")])
        self.assertEqual((self.dst / "FolderMod" / "inner" / "data.bin").read_text(encoding="utf-8"), "data")

    def test_an_existing_target_is_reported_instead_of_being_replaced(self):
        self._write("Weapon.pak", "new")
        (self.dst / "Weapon.pak").write_text("old", encoding="utf-8")

        ok, message = apply_mods_batch(self._mods())[0]

        self.assertFalse(ok)
        self.assertIn("Target already exists", message)
        self.assertEqual((self.dst / "Weapon.pak").read_text(encoding="utf-8"), "old")

    def test_overwrite_replaces_the_existing_target(self):
        self._write("Weapon.pak", "new")
        (self.dst / "Weapon.pak").write_text("old", encoding="utf-8")

        ok, _message = apply_mods_batch(self._mods(), True)[0]

        self.assertTrue(ok)
        self.assertEqual((self.dst / "Weapon.pak").read_text(encoding="utf-8"), "new")

    def test_uninstalling_deletes_the_copy_and_keeps_the_source(self):
        self._write("Weapon.pak", "payload")
        mods = self._mods()
        apply_mods_batch(mods)

        ok, _message = deactivate_mod(self._mods()[0])

        self.assertTrue(ok)
        self.assertFalse((self.dst / "Weapon.pak").exists())
        self.assertEqual((self.src / "Weapon.pak").read_text(encoding="utf-8"), "payload")

    def test_uninstalling_deletes_a_copied_folder(self):
        folder = self.src / "FolderMod"
        folder.mkdir()
        (folder / "data.bin").write_text("data", encoding="utf-8")
        apply_mods_batch(self._mods(mod_extensions="folders"))

        ok, _message = deactivate_mod(self._mods(mod_extensions="folders")[0])

        self.assertTrue(ok)
        self.assertFalse((self.dst / "FolderMod").exists())
        self.assertTrue((self.src / "FolderMod" / "data.bin").exists())

    def test_installing_a_group_copies_every_member(self):
        self._write_group("Weapon")

        results = apply_mods_batch(self._mods(mod_group_extensions=".pak,.utoc,.ucas"))

        self.assertEqual(results, [(True, "OK")])
        for suffix in GROUP_SUFFIXES:
            self.assertTrue((self.dst / f"Weapon{suffix}").exists(), suffix)

    def test_uninstalling_a_group_removes_every_member(self):
        self._write_group("Weapon")
        group = {"mod_group_extensions": ".pak,.utoc,.ucas"}
        apply_mods_batch(self._mods(**group))

        ok, _message = deactivate_mod(self._mods(**group)[0])

        self.assertTrue(ok)
        self.assertEqual(list(self.dst.iterdir()), [])
        self.assertEqual(len(list(self.src.iterdir())), len(GROUP_SUFFIXES))

    def test_a_half_installed_group_completes_without_an_error(self):
        self._write_group("Weapon", "payload")
        group = {"mod_group_extensions": ".pak,.utoc,.ucas"}
        (self.dst / "Weapon.pak").write_text("payload", encoding="utf-8")

        mod = self._mods(**group)[0]
        self.assertFalse(mod.installed)
        results = apply_mods_batch([mod])

        self.assertEqual(results, [(True, "OK")])
        self.assertTrue(self._mods(**group)[0].installed)

    def test_overwrite_replaces_the_stale_member_of_a_half_installed_group(self):
        self._write_group("Weapon", "fresh")
        group = {"mod_group_extensions": ".pak,.utoc,.ucas"}
        (self.dst / "Weapon.utoc").write_text("stale", encoding="utf-8")

        results = apply_mods_batch(self._mods(**group), True)

        self.assertEqual(results, [(True, "OK")])
        for suffix in GROUP_SUFFIXES:
            self.assertEqual((self.dst / f"Weapon{suffix}").read_text(encoding="utf-8"), "fresh", suffix)

    def test_existing_targets_lists_every_member_a_copy_install_would_replace(self):
        self._write_group("Weapon")
        group = {"mod_group_extensions": ".pak,.utoc,.ucas"}
        (self.dst / "Weapon.pak").touch()
        (self.dst / "Weapon.ucas").touch()

        names = existing_targets(self._mods(**group))

        self.assertEqual(sorted(names), ["Weapon.pak", "Weapon.ucas"])
        self.assertIn("Weapon.pak", overwrite_message(names))
        self.assertIn("2 file(s) already exist", overwrite_message(names))

    def test_a_link_profile_never_reports_overwrite_targets(self):
        self._write("Weapon.pak")
        (self.dst / "Weapon.pak").touch()

        self.assertEqual(existing_targets(self._mods(install_mode="link")), [])

    def test_a_link_profile_still_installs_through_the_link_layer(self):
        self._write("Weapon.pak")

        with patch("mod_manager.mods._link_files", return_value=[(True, "OK")]) as link_files:
            results = apply_mods_batch(self._mods(install_mode="link"))

        self.assertEqual(results, [(True, "OK")])
        self.assertEqual([f.src.name for f in link_files.call_args[0][0]], ["Weapon.pak"])
        self.assertFalse((self.dst / "Weapon.pak").exists())


if __name__ == "__main__":
    unittest.main()
