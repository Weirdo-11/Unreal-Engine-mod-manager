from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from .theme import tokens

STANDARD_ICONS = {
    "add": "SP_DialogApplyButton",
    "back": "SP_ArrowBack",
    "clear": "SP_DialogResetButton",
    "delete": "SP_TrashIcon",
    "folder": "SP_DirOpenIcon",
    "forward": "SP_ArrowForward",
    "image": "SP_FileIcon",
    "import": "SP_FileDialogNewFolder",
    "install": "SP_DialogApplyButton",
    "list": "SP_FileDialogDetailedView",
    "menu": "SP_TitleBarMenuButton",
    "open": "SP_DirIcon",
    "remove": "SP_DialogCancelButton",
    "save": "SP_DialogSaveButton",
    "search": "SP_FileDialogContentsView",
    "toggle": "SP_BrowserReload",
    "uninstall": "SP_DialogDiscardButton",
}

FALLBACK_ICON = "SP_FileIcon"


def standard_icon(name: str, style=None) -> QtGui.QIcon:
    style = style or QtWidgets.QApplication.style()
    pixmap_name = STANDARD_ICONS.get(name, FALLBACK_ICON)
    return style.standardIcon(getattr(QtWidgets.QStyle, pixmap_name))


def _painter(pixmap: QtGui.QPixmap) -> QtGui.QPainter:
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    return painter


def _transparent_pixmap(size: int) -> QtGui.QPixmap:
    pixmap = QtGui.QPixmap(size, size)
    pixmap.fill(QtCore.Qt.transparent)
    return pixmap


def _round_pen(color, width: float) -> QtGui.QPen:
    return QtGui.QPen(QtGui.QColor(color), width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)


def _path(points) -> QtGui.QPainterPath:
    path = QtGui.QPainterPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    return path


def check_icon(color, size: int = tokens.ICON_SIZE, transparent: bool = False) -> QtGui.QIcon:
    pixmap = _transparent_pixmap(size)
    if not transparent:
        painter = _painter(pixmap)
        painter.setPen(_round_pen(color, max(tokens.CHECK_PEN_MIN, size * tokens.CHECK_PEN_RATIO)))
        painter.drawPath(_path([(size * x, size * y) for x, y in tokens.CHECK_PATH]))
        painter.end()
    return QtGui.QIcon(pixmap)


def sort_direction_icon(descending: bool, color, size: int = tokens.ICON_SIZE) -> QtGui.QIcon:
    pixmap = _transparent_pixmap(size)
    painter = _painter(pixmap)
    painter.setPen(_round_pen(color, tokens.SORT_ARROW_PEN))
    x = size // 2
    head = tokens.SORT_ARROW_HEAD
    margin = tokens.SORT_ARROW_MARGIN
    head_y = tokens.SORT_ARROW_HEAD_Y
    if descending:
        tip = size - margin - 1
        painter.drawLine(x, margin, x, tip)
        painter.drawLine(x, tip, x - head, size - head_y)
        painter.drawLine(x, tip, x + head, size - head_y)
    else:
        tip = margin + 1
        painter.drawLine(x, size - margin, x, tip)
        painter.drawLine(x, tip, x - head, head_y)
        painter.drawLine(x, tip, x + head, head_y)
    painter.end()
    return QtGui.QIcon(pixmap)


def state_icon(active: bool, palette, size: int = tokens.STATE_ICON_SIZE) -> QtGui.QIcon:
    pixmap = _transparent_pixmap(size)
    painter = _painter(pixmap)
    painter.setPen(_round_pen(palette.state_ok if active else palette.state_bad, tokens.STATE_ICON_PEN))
    if active:
        painter.drawPath(_path(tokens.STATE_CHECK_PATH))
    else:
        for (x1, y1), (x2, y2) in tokens.STATE_CROSS_PATH:
            painter.drawLine(x1, y1, x2, y2)
    painter.end()
    return QtGui.QIcon(pixmap)
