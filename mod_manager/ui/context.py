from __future__ import annotations

from typing import Callable

from ..storage import save_config
from .task_runner import TaskRunner
from .theme import tokens
from .theme.manager import ThemeManager


class AppContext:
    def __init__(self, cfg: dict, theme: ThemeManager, runner: TaskRunner):
        self.cfg = cfg
        self.theme = theme
        self.runner = runner

    @property
    def palette(self):
        return self.theme.palette

    @property
    def busy(self) -> bool:
        return self.runner.busy

    @property
    def status_text(self) -> str:
        return self.runner.status_text

    def replace_config(self, cfg: dict) -> dict:
        self.cfg = cfg
        self.theme.cfg = cfg
        return cfg

    def save(self, **values) -> None:
        self.cfg.update(values)
        save_config(self.cfg)

    def run(self, label: str, worker: Callable, done: Callable | None = None, file_key: str = "global") -> None:
        self.runner.run(label, worker, done, file_key)

    def page_size(self) -> int:
        return max(1, tokens.to_int(self.cfg.get("page_size"), 10))

    def tile_size(self) -> int:
        return tokens.clamp_tile_size(self.cfg.get("tile_size"))
