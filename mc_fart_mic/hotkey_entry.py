import keyboard
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QEventLoop, pyqtSlot
from PyQt5.QtWidgets import QWidget, QFileDialog, qApp, QStyle

from message_boxes import show_simple_warning_message, show_simple_info_message


# Formats that are sure to be supported on all backends, depending on user OS many more might be supported.
SUPPORTED_AUDIO_FORMATS = ("mp3", "wav")


class HotkeyEntryUI(QWidget):
    HOTKEY_TEXT_LISTEN_PLACEHOLDER = "press something on your keyboard"

    def __init__(self, main_menu):
        super(HotkeyEntryUI, self).__init__()
        uic.loadUi("layouts/add_hotkey.ui", self)
        self.setFixedSize(self.size())

        self._main_menu = main_menu
        self._currently_listening_for_hotkey = False

        self.button_listen_hotkey.clicked.connect(self.listen_hotkey)
        self.button_clear_hotkey_entry.clicked.connect(self.clear_hotkey_entry)

        self.button_help_copy.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.button_help_copy.clicked.connect(self.show_help_copy_sound_file)

        self.select_sound_file_button.setIcon(qApp.style().standardIcon(QStyle.SP_DirLinkIcon))
        self.select_sound_file_button.clicked.connect(self.open_filename_dialog)

        self.button_save_hotkey.clicked.connect(self.save_hotkey)

    def listen_hotkey(self):
        if self._currently_listening_for_hotkey:
            return

        self._currently_listening_for_hotkey = True
        self.hotkey_line_edit.setText(self.HOTKEY_TEXT_LISTEN_PLACEHOLDER)
        # If we don't sleep here the above line edit text does update on time
        self.non_blocking_sleep(10)

        hotkey = keyboard.read_hotkey()
        self.hotkey_line_edit.setText(hotkey)
        self._currently_listening_for_hotkey = False

    @classmethod
    def non_blocking_sleep(cls, ms: int):
        loop = QEventLoop()
        QTimer.singleShot(ms, loop.quit)
        loop.exec_()

    @pyqtSlot()
    def clear_hotkey_entry(self):
        self.hotkey_line_edit.clear()

    @pyqtSlot()
    def show_help_copy_sound_file(self):
        show_simple_info_message(
            "If this box is checked then selected sound file will be copied to /sounds directory which can be "
            "found in the same directory as this program.\nThis helps keeping all sound files in one place."
        )

    @pyqtSlot()
    def open_filename_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        extensions = " ".join(f"*.{ext}" for ext in SUPPORTED_AUDIO_FORMATS)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select sound file",
            directory="",
            filter=f"Sound Files ({extensions});;All Files (*)",
            options=options
        )

        if file_path:
            self.sound_file_line_edit.setText(file_path)

    def save_hotkey(self):
        if self.hotkey_line_edit.text() in ("", self.HOTKEY_TEXT_LISTEN_PLACEHOLDER):
            return show_simple_warning_message("Please enter a hotkey.")
        elif not self.sound_file_line_edit.text():
            return show_simple_warning_message("Please select a sound file.")

        self._main_menu.new_hotkey_entry(self.hotkey_line_edit.text(), self.sound_file_line_edit.text())
        self.hide()
