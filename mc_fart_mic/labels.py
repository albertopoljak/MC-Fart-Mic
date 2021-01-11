from typing import Callable

from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMouseEvent


class QLabelClick(QLabel):
    """
    Simple QLabel for which you can define left and right click actions.

    Functions tied to clicks need to take one argument - QLabel representing the clicked label.
    """
    __slots__ = ("_left_click_action", "_right_click_action")

    def __init__(
            self,
            *args,
            left_click_action: Callable[[QLabel], None] = None,
            right_click_action: Callable[[QLabel], None] = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self._left_click_action = left_click_action
        self._right_click_action = right_click_action

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._left_click_action is not None and event.button() == QtCore.Qt.LeftButton:
            self._left_click_action(self)
        elif self._right_click_action is not None and event.button() == QtCore.Qt.RightButton:
            self._right_click_action(self)


class EntryLabel(QLabelClick):
    """Label that will be stacked in rows so it has argument entry_row to save the position."""
    def __init__(self, *args, entry_row: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.entry_row = entry_row


class HoverEntryLabel(EntryLabel):
    """Simple hover label that changes color to green on mouse hover and resets color on mouse exit."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enable_hover_events = True

    def enterEvent(self, event: QtCore.QEvent):
        if self._enable_hover_events:
            self.setStyleSheet("QLabel { color: green;}")

    def leaveEvent(self, event: QtCore.QEvent):
        if self._enable_hover_events:
            self.setStyleSheet("")
