from typing import Callable

from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QMouseEvent
from PyQt5 import QtCore


class PushButtonEntry(QPushButton):
    """Simple PushButton that has ID attached to it for whatever identification purposes you'd need."""
    __slots__ = ("id",)

    def __init__(self, button_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = button_id


class QLabelEntry(QLabel):
    """
    Simple QLabel for which you can define left and right click actions.
    It also changes text color to green on mouse hover.
    """
    __slots__ = ("entry_row", "_left_click_action", "_right_click_action")

    def __init__(
            self,
            *args,
            entry_row: int,
            left_click_action: Callable = None,
            right_click_action: Callable = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.entry_row = entry_row
        self._left_click_action = left_click_action
        self._right_click_action = right_click_action

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._left_click_action is not None and event.button() == QtCore.Qt.LeftButton:
            self._left_click_action(self)
        elif self._right_click_action is not None and event.button() == QtCore.Qt.RightButton:
            self._right_click_action(self)

    def enterEvent(self, event: QtCore.QEvent):
        self.setStyleSheet("QLabel { color: green;}")

    def leaveEvent(self, event: QtCore.QEvent):
        self.setStyleSheet("")
