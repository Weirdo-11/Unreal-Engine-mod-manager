from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ModFile:
    src: Path
    dest: Path
    is_dir: bool

@dataclass
class ModItem:
    name: str
    src: Path
    dest: Path
    is_dir: bool
    installed: bool
    files: tuple[ModFile, ...] = ()
    copy_install: bool = False

    @property
    def install_files(self) -> tuple[ModFile, ...]:
        """Every file the mod installs; a plain mod installs itself alone."""
        return self.files or (ModFile(self.src, self.dest, self.is_dir),)
