from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6 import QtCore, QtGui, QtWidgets

from ..theme import tokens
from .style_utils import LINK, apply_margins, clear_layout, fixed_size_policy, set_variant


class DetailImageLabel(QtWidgets.QLabel):
    def __init__(self, pixmap: QtGui.QPixmap, parent=None):
        super().__init__(parent)
        self._source_pixmap = pixmap
        self._target_size = QtCore.QSize(1, 1)
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.setMinimumWidth(0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_scaled_pixmap()

    def update_scaled_pixmap(self, size: QtCore.QSize | None = None) -> None:
        if self._source_pixmap.isNull():
            return
        if size is not None:
            self._target_size = size
        target_width = self._target_size.width() if self._target_size.width() > 1 else self.width()
        if target_width <= 1 and self.parentWidget():
            target_width = self.parentWidget().width()
        target_height = self._target_size.height() if self._target_size.height() > 1 else self._source_pixmap.height()
        scaled = self._source_pixmap.scaled(
            max(1, target_width),
            max(1, target_height),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.setPixmap(scaled)
        self.setFixedHeight(scaled.height())


def detail_name_label(text: str, parent=None) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(text, parent)
    label.setMinimumWidth(tokens.DETAIL_LABEL_MIN_WIDTH)
    label.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
    return label


def path_button(path: Path, on_click: Callable, parent=None) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton(str(path), parent)
    set_variant(button, LINK)
    button.setFlat(True)
    button.setCursor(QtCore.Qt.PointingHandCursor)
    button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    button.clicked.connect(lambda _checked=False, target=Path(path): on_click(target))
    return button


def action_button(text: str, icon: QtGui.QIcon, tooltip: str, on_click: Callable, parent=None) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton(text, parent)
    button.setIcon(icon)
    button.setToolTip(tooltip)
    button.clicked.connect(lambda _checked=False: on_click())
    return fixed_size_policy(button)


class DetailPanel(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.frame = QtWidgets.QWidget()
        self.frame.setAutoFillBackground(True)
        set_variant(self.frame, "panel")
        self.layout = apply_margins(
            QtWidgets.QVBoxLayout(self.frame),
            margins=tokens.DETAIL_MARGIN,
            spacing=tokens.SPACE_LG,
        )
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.setWidgetResizable(True)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setWidget(self.frame)

    def clear(self) -> None:
        clear_layout(self.layout)

    def add_widget(self, widget: QtWidgets.QWidget) -> QtWidgets.QWidget:
        self.layout.addWidget(widget)
        return widget

    def add_row(self, *widgets, stretch_last: bool = False, trailing_stretch: bool = False):
        row = apply_margins(QtWidgets.QHBoxLayout(), margins=None)
        for index, widget in enumerate(widgets):
            last = index == len(widgets) - 1
            row.addWidget(widget, 1 if stretch_last and last else 0)
        if trailing_stretch:
            row.addStretch(1)
        self.layout.addLayout(row)
        return row

    def add_text_row(self, label: str, value: str) -> None:
        value_label = QtWidgets.QLabel(value)
        value_label.setWordWrap(True)
        self.add_row(detail_name_label(label), value_label, stretch_last=True)

    def add_stretch(self) -> None:
        self.layout.addStretch(1)

    def available_width(self) -> int:
        margins = self.layout.contentsMargins()
        width = self.viewport().width() or self.width()
        return max(1, width - margins.left() - margins.right())

    def image_target_size(self, image: DetailImageLabel | None = None) -> QtCore.QSize:
        margins = self.layout.contentsMargins()
        viewport_height = self.viewport().height() or self.height()
        top = image.y() if image is not None and image.y() > 0 else margins.top()
        return QtCore.QSize(
            max(1, self.available_width() - tokens.DETAIL_IMAGE_INSET),
            max(1, viewport_height - top - margins.bottom() - tokens.DETAIL_IMAGE_INSET),
        )

    def rescale_images(self) -> None:
        for image in self.frame.findChildren(DetailImageLabel):
            image.update_scaled_pixmap(self.image_target_size(image))

    def dates_fit_on_one_row(self, first: str, second: str, available_width: int | None = None) -> bool:
        if available_width is None:
            available_width = self.available_width()
        metrics = self.frame.fontMetrics()
        needed = (
            tokens.DETAIL_LABEL_MIN_WIDTH * 2
            + metrics.horizontalAdvance(first)
            + metrics.horizontalAdvance(second)
            + tokens.DETAIL_DATES_SPACING
        )
        return available_width >= needed
