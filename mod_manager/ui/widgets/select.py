from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ..theme import tokens


class SelectBox(QtWidgets.QComboBox):
    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(
            QtGui.QPen(
                self.palette().color(QtGui.QPalette.ButtonText),
                tokens.COMBO_CHEVRON_PEN,
                QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap,
                QtCore.Qt.RoundJoin,
            )
        )
        center = QtCore.QPoint(
            self.width() - tokens.COMBO_CHEVRON_RIGHT_INSET,
            self.height() // 2,
        )
        path = QtGui.QPainterPath()
        path.moveTo(center.x() - tokens.COMBO_CHEVRON_HALF_WIDTH, center.y() - tokens.COMBO_CHEVRON_HALF_HEIGHT)
        path.lineTo(center.x(), center.y() + tokens.COMBO_CHEVRON_HALF_HEIGHT)
        path.lineTo(center.x() + tokens.COMBO_CHEVRON_HALF_WIDTH, center.y() - tokens.COMBO_CHEVRON_HALF_HEIGHT)
        painter.drawPath(path)


def select_box(parent=None, editable: bool = False) -> SelectBox:
    box = SelectBox(parent)
    box.setEditable(editable)
    return box
