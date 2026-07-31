"""Compatibility shim. The GUI lives in mod_manager.ui."""

from __future__ import annotations

from .ui import qt_available, run_gui


def __getattr__(name: str):
    if name in {"ModManagerGui", "start"}:
        from .ui import app
        return getattr(app, name)
    raise AttributeError(name)


__all__ = ["ModManagerGui", "qt_available", "run_gui", "start"]
