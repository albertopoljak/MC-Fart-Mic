import keyboard
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QEventLoop, pyqtSlot
from PyQt5.QtWidgets import QWidget, QFileDialog, qApp, QStyle

from constants import SURE_SUPPORTED_AUDIO_FORMATS, POSSIBLE_AUDIO_FORMATS
from message_boxes import show_simple_info_message, show_simple_warning_message


class AddHotkeyUI(QWidget):
    HOTKEY_TEXT_LISTEN_PLACEHOLDER = "press something on your keyboard"

    def __init__(self, main_menu):
        super(AddHotkeyUI, self).__init__()
        uic.loadUi("layouts/add_hotkey.ui", self)
        self.setFixedSize(self.size())

        self._main_menu = main_menu
        self._currently_listening_for_hotkey = False

        self.button_listen_hotkey.clicked.connect(self.listen_hotkey)
        self.button_clear_hotkey_entry.clicked.connect(self.clear_hotkey_entry)

        self.help_select_file.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_select_file.clicked.connect(self.show_help_select_file)

        self.select_sound_file_button.setIcon(qApp.style().standardIcon(QStyle.SP_FileLinkIcon))
        self.select_sound_file_button.clicked.connect(self.select_filename_dialog)

        self.select_sound_directory_button.setIcon(qApp.style().standardIcon(QStyle.SP_DirLinkIcon))
        self.select_sound_directory_button.clicked.connect(self.select_directory_dialog)

        self.button_save_hotkey.clicked.connect(self.save_hotkey)

    def listen_hotkey(self):
        if self._currently_listening_for_hotkey:
            return

        self._currently_listening_for_hotkey = True
        self.hotkey_line_edit.setText(self.HOTKEY_TEXT_LISTEN_PLACEHOLDER)
        # If we don't sleep here the above line edit text doesn't update on time
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
        # multiple calls to read_hotkey build upon previous entries, so we clear them here
        keyboard.stash_state()
        self.hotkey_line_edit.clear()

    @pyqtSlot()
    def show_help_select_file(self):
        show_simple_info_message(
            "When selecting a single file default filter is only .wav and .mp3 files "
            "because those are supported on all systems.\n"
            "However your system can and probably does support many more.\n"
            "If you'd like to select some other audio file other than those 2 formats then change filter in the "
            "explorer window to 'All sound files'\n"
            "Be sure to test those other formats, if they don't play they are not supported on your system.\n\n"
            "Same works with selecting directories, if some sound files inside are not supported "
            "they will just not play."
        )

    @pyqtSlot()
    def select_filename_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        sure_supported_extensions = " ".join(f"*{ext}" for ext in SURE_SUPPORTED_AUDIO_FORMATS)
        possible_supported_extensions = " ".join(f"*{ext}" for ext in POSSIBLE_AUDIO_FORMATS)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select sound file",
            filter=(
                f"Sure supported sound files ({sure_supported_extensions});;"
                f"All sound files ({possible_supported_extensions})"
                ),
            options=options
        )

        if file_path:
            self.sound_file_line_edit.setText(file_path)

    @pyqtSlot()
    def select_directory_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog | QFileDialog.ShowDirsOnly

        directory_path = str(QFileDialog.getExistingDirectory(self, "Select Directory", options=options))

        if directory_path:
            self.sound_file_line_edit.setText(directory_path)

    def save_hotkey(self):
        if self.hotkey_line_edit.text() in ("", self.HOTKEY_TEXT_LISTEN_PLACEHOLDER):
            return show_simple_warning_message("Please enter a hotkey.")
        elif not self.sound_file_line_edit.text():
            return show_simple_warning_message("Please select a sound file.")

        self._main_menu.new_hotkey_entry(self.hotkey_line_edit.text(), self.sound_file_line_edit.text())
        self.hide()
