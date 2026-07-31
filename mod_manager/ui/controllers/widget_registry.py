from __future__ import annotations

ACTIONS = "actions"
SELECTION = "selection"


class WidgetRegistry:
    def __init__(self):
        self._groups: dict[str, list] = {}

    def add(self, group: str, widget) -> object:
        if widget is not None:
            self._groups.setdefault(group, []).append(widget)
        return widget

    def extend(self, group: str, widgets) -> None:
        for widget in widgets:
            self.add(group, widget)

    def widgets(self, group: str) -> list:
        return list(self._groups.get(group, ()))

    def groups(self) -> list[str]:
        return list(self._groups)

    def set_enabled(self, group: str, enabled: bool) -> None:
        for widget in self.widgets(group):
            widget.setEnabled(bool(enabled))
