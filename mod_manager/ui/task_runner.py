from __future__ import annotations

from typing import Callable

from PySide6 import QtCore

from ..workers import WorkerPool
from .theme import tokens

GLOBAL_KEY = "global"


class TaskRunner(QtCore.QObject):
    busyChanged = QtCore.Signal(bool)
    statusChanged = QtCore.Signal(str)
    failed = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.busy = False
        self.status_text = ""
        self._pool = WorkerPool()
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.poll)

    def set_status(self, text: str) -> None:
        self.status_text = text
        self.statusChanged.emit(text)

    def set_busy(self, busy: bool, text: str = "") -> None:
        self.busy = busy
        self.busyChanged.emit(busy)
        if text:
            self.set_status(text)

    def run(self, label: str, worker: Callable, done: Callable | None = None, file_key: str = GLOBAL_KEY) -> None:
        self.set_busy(True, label)

        def callback(result, error):
            self.set_busy(False)
            if error:
                self.failed.emit(str(error))
                return
            if done:
                done(result)

        self._pool.submit(file_key, worker, callback=callback)
        self._timer.start(tokens.WORKER_POLL_MS)

    def poll(self) -> None:
        polled = self._pool.poll()
        self._pool.fire_callbacks(polled)
        if not self._pool.has_work():
            self._timer.stop()

    def shutdown(self) -> None:
        self._timer.stop()
        self._pool.shutdown()
