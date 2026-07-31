from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class ModListView(QtWidgets.QListView):
    zoomRequested = QtCore.Signal(int)

    def wheelEvent(self, event) -> None:
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoomRequested.emit(1 if event.angleDelta().y() > 0 else -1)
            event.accept()
            return
        super().wheelEvent(event)
