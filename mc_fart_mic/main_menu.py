import sys
import json
import random
import logging
import traceback
from typing import Type
from pathlib import Path

import keyboard
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import (
    QMainWindow, QFormLayout, QGroupBox, qApp, QAction,
    QApplication, QMenu, QVBoxLayout, QSystemTrayIcon, QStyle
)

import message_boxes
from config import Config
from settings import SettingsUi
from add_hotkey import AddHotkeyUI
from labels import HoverEntryLabel
from player_pool import PlayerPool, PlayerPoolManager
from constants import GITHUB_REPO_LINK, PROGRAM_VERSION, POSSIBLE_AUDIO_FORMATS


logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s %(name)s - %(message)s")


class HotkeyListenerThread(QtCore.QThread):
    """Qt friendly thread for listening keyboard events."""
    def run(self):
        keyboard.wait("esc")


class MainWindowUi(QMainWindow):
    LAYOUTS_DIRECTORY = Path("layouts")
    PROFILES_DIRECTORY = Path("profiles")
    DEFAULT_PROFILE_NAME = "default"

    def __init__(self):
        # Register exception handler, at the very beginning so it doesn't miss any exceptions if we register it later
        self._backup_excepthook = sys.excepthook
        sys.excepthook = self._exception_hook

        super(MainWindowUi, self).__init__()
        uic.loadUi(self.LAYOUTS_DIRECTORY / "main_menu.ui", self)
        self.setFixedSize(self.size())

        self.application_icon = QStyle.SP_TitleBarMenuButton
        self.setWindowIcon(qApp.style().standardIcon(self.application_icon))

        self.player_pool_manager = PlayerPoolManager(PlayerPool(), PlayerPool())

        self.settings_ui = SettingsUi(self.player_pool_manager)
        self.add_hotkey_ui = AddHotkeyUI(self)

        self.menu_settings.triggered.connect(self.settings_ui.show)
        self.menu_help.triggered.connect(self.on_menu_help_click)
        self.menu_about.triggered.connect(self.on_menu_about_click)
        self.menu_exit.triggered.connect(self.on_menu_exit_click)
        self.button_load_profile.clicked.connect(self.on_button_load_profile_click)
        self.button_create_profile.clicked.connect(self.on_button_create_profile_click)
        self.button_add_hotkey.clicked.connect(self.open_hot_key_entry_window)

        self.populate_profiles_combo_box()
        Config.register_combobox(self.combo_box_profile)
        current_combo_box_profile = self.combo_box_profile.currentText()
        self.profile = self.load_profile_json(current_combo_box_profile) if current_combo_box_profile else {}

        self.hotkey_entries_area = QFormLayout()
        self.initialize_scroll_area(self.hotkey_entries_area)

        self.refresh_hotkeys()
        self.hotkey_listener_worker = HotkeyListenerThread()
        self.hotkey_listener_worker.start()

        self.show()

        self.tray_icon = self.create_tray_icon()
        self.tray_icon.show()

    def changeEvent(self, event: QtCore.QEvent):
        """On minimize event we want to move it to tray, if it's enabled in options."""
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.settings_ui.check_minimize_to_tray.isChecked() and QtCore.Qt.WindowMinimized:
                event.ignore()
                self.hide()
                self.send_tray_message()

    def closeEvent(self, event: QtCore.QEvent):
        """On close event we want to move it to tray, if it's enabled in options."""
        if self.settings_ui.check_minimize_on_close.isChecked():
            event.ignore()
            self.hide()
            self.send_tray_message()

    def send_tray_message(self):
        """Sends tray message about program being minimized to tray, if it's enabled in options."""
        if self.settings_ui.check_show_try_msg_on_minimize.isChecked():
            self.tray_icon.showMessage(
                self.windowTitle(), "Application was minimized to Tray", QSystemTrayIcon.Information, 1000
            )

    def populate_profiles_combo_box(self):
        profile_names = [str(path.stem) for path in self.PROFILES_DIRECTORY.glob("**/*.json")]
        if not profile_names:
            self.combo_box_profile.addItem(self.DEFAULT_PROFILE_NAME)
        else:
            self.combo_box_profile.addItems(profile_names)

    def load_profile_json(self, profile_name: str) -> dict:
        """Load profile dataa from saved json."""
        try:
            with open(self.PROFILES_DIRECTORY / f"{profile_name}.json", "r") as file:
                return json.load(file)
        except Exception:  # noqa PyBroadException
            if profile_name == self.DEFAULT_PROFILE_NAME:
                # Hot-fix when app is initially opened there will be no profiles
                return {}
            else:
                return message_boxes.show_simple_traceback_message(f"Can't load profile '{profile_name}'.")

    def save_profile_json(self, profile_name: str) -> None:
        """Save current profile data to json file."""
        try:
            with open(self.PROFILES_DIRECTORY / f"{profile_name}.json", "w") as file:
                json.dump(self.profile, file, indent=4)
        except Exception:  # noqa PyBroadException
            return message_boxes.show_simple_traceback_message(f"Failed to save profile '{profile_name}'.")

    @QtCore.pyqtSlot()
    def on_button_load_profile_click(self):
        self.player_pool_manager.stop_all_playback()

        selected_profile = self.combo_box_profile.currentText()
        self.profile = self.load_profile_json(selected_profile)
        self.clear_scroll_area()
        self.populate_scroll_area()
        self.refresh_hotkeys()
        message_boxes.show_simple_success_message(f"Profile '{selected_profile}' loaded successfully.")

    @QtCore.pyqtSlot()
    def on_button_create_profile_click(self):
        profile_name = self.line_edit_create_profile.text()
        if not profile_name:
            return message_boxes.show_simple_warning_message("Can't create profile with empty name!")

        self.player_pool_manager.stop_all_playback()

        self.profile = {}
        self.combo_box_profile.insertItem(0, profile_name)
        self.combo_box_profile.setCurrentIndex(0)

        self.clear_scroll_area()
        self.refresh_hotkeys()
        self.save_profile_json(profile_name)

        message_boxes.show_simple_success_message(f"Profile '{profile_name}' created successfully.")

    @QtCore.pyqtSlot()
    def open_hot_key_entry_window(self):
        self.add_hotkey_ui.show()

    @QtCore.pyqtSlot()
    def hotkey_entry_left_click(self, label: HoverEntryLabel):
        self.play_sound(label.text())

    @QtCore.pyqtSlot()
    def hotkey_entry_right_click(self, _label: HoverEntryLabel):
        message_boxes.show_simple_info_message("Editing not yet implemented.")  # TODO

    def play_sound(self, sound_path: str):
        path = Path(sound_path)
        if path.is_dir():
            files = [file for file in path.rglob("**/*") if file.is_file() and file.suffix in POSSIBLE_AUDIO_FORMATS]
            random_sound = str(random.choice(files))
            url = QtCore.QUrl.fromLocalFile(QtCore.QDir.current().absoluteFilePath(random_sound))
        else:
            url = QtCore.QUrl.fromLocalFile(QtCore.QDir.current().absoluteFilePath(sound_path))

        self.player_pool_manager.play(
            url=url,
            also_play_on_additional=self.settings_ui.check_enable_additional_playback_device.isChecked()
        )

    @QtCore.pyqtSlot()
    def on_menu_help_click(self):
        help_msg = message_boxes.message_box_constructor(
            "You can find help instructions in repository readme.",
            title="Help",
            informative_text="Repository is open source, click show details to see the link.",
            detailed_text=f"Source code:\n{GITHUB_REPO_LINK}",
        )
        help_msg.exec_()

    @QtCore.pyqtSlot()
    def on_menu_about_click(self):
        about_msg = message_boxes.message_box_constructor(
            "Simple program to help in organizing and playing sound files.",
            title="About",
            informative_text=(
                "Made out of a idea to  play sounds to your microphone (using 3d party virtual mixer driver) so that "
                "when you press certain hot-key the selected sound will play in your game/chat mic."
            ), detailed_text=(
                F"Source code: {GITHUB_REPO_LINK}k\n"
                f"Version: {PROGRAM_VERSION}\n"
                "Author: BrainDead\n"
                f"License: GPLv3"
            )
        )
        about_msg.exec_()

    @QtCore.pyqtSlot()
    def on_menu_exit_click(self):
        self.hotkey_listener_worker.terminate()
        sys.exit()

    def initialize_scroll_area(self, form_layout: QFormLayout):
        """
        Loads saved hotkey-sound values and populates scroll area with them.
        This should be called once at program start.
        """
        group_box = QGroupBox()
        self.populate_scroll_area()
        group_box.setLayout(form_layout)
        self.scroll_area_main.setWidget(group_box)
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area_main)

    def populate_scroll_area(self):
        """Populates scroll area with hotkey/sound labels based on currently loaded profile."""
        for hotkey, sound_path in self.profile.items():
            self.add_hotkey_to_scrollbar(f"{hotkey:<8}", sound_path)

    def clear_scroll_area(self):
        for _ in range(self.hotkey_entries_area.rowCount()):
            self.hotkey_entries_area.removeRow(0)

    def refresh_hotkeys(self):
        """
        Registers hotkeys based on currently loaded profile data.
        Any existing hotkey listeners are cleared.
        """
        keyboard.unhook_all()
        for hotkey, sound_path in self.profile.items():
            keyboard.add_hotkey(hotkey, self.play_sound, args=(sound_path,))

    def new_hotkey_entry(self, hotkey: str, sound_path: str):
        continue_adding = True
        if self.check_duplicate_hotkey(hotkey):
            continue_adding = message_boxes.show_simple_confirmation_message(
                "That hotkey is already registered.\n"
                "If you add it you will have multiple files playing for single hotkey.\n"
                "Continue adding?"
            )
        elif self.check_duplicate_path(sound_path):
            continue_adding = message_boxes.show_simple_confirmation_message(
                "That path is already registered.\n"
                "If you add it you will have multiple hotkeys for the same path.\n"
                "Continue adding?"
            )

        if not continue_adding:
            return

        self.add_hotkey_to_scrollbar(hotkey, sound_path)
        self.profile[hotkey] = sound_path
        keyboard.add_hotkey(hotkey, self.play_sound, args=(sound_path,))

        # Auto save at end
        current_profile = self.combo_box_profile.currentText()
        self.save_profile_json(current_profile)

    def add_hotkey_to_scrollbar(self, hotkey: str, sound_path: str):
        """This only adds hotkey/path labels to scrollbar area. Aka it only deals with visual things."""
        insert_row = 0
        label_hotkey = HoverEntryLabel(hotkey, entry_row=insert_row)
        label_sound_file = HoverEntryLabel(
            sound_path, entry_row=insert_row,
            left_click_action=self.hotkey_entry_left_click, right_click_action=self.hotkey_entry_right_click
        )

        # TODO migrate to class?
        font = label_hotkey.font()
        font.setPointSize(11)
        label_hotkey.setFont(font)
        label_sound_file.setFont(font)

        self.hotkey_entries_area.addRow(label_hotkey, label_sound_file)

    def check_duplicate_hotkey(self, hotkey: str) -> bool:
        return hotkey in self.profile

    def check_duplicate_path(self, path: str) -> bool:
        return path in self.profile.values()

    def create_tray_icon(self) -> QSystemTrayIcon:
        """Creates tray icon and available options when icon is right clicked."""
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setIcon(self.style().standardIcon(self.application_icon))

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.showNormal)

        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(qApp.quit)

        tray_menu = QMenu()
        for action in (show_action, hide_action, quit_action):
            tray_menu.addAction(action)

        tray_icon.setContextMenu(tray_menu)
        return tray_icon

    def _exception_hook(self, exc_type: Type[BaseException], exc_value: Exception, exc_traceback: traceback):
        """Logs traceback to logger and shows a error message."""
        self._backup_excepthook(exc_type, exc_value, exc_traceback)
        exception_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logging.error(exception_message)
        message_boxes.show_simple_traceback_message(
            message_text=(
                "Uh oh, a wild exception!\n"
                "Check details below and report this to author if you wish (Application/about)."
            ),
            custom_traceback_msg=exception_message
        )


if __name__ == "__main__":
    try:
        # Make directory in case of pyinstaller or similar.
        # Note that layouts should be packed in the bundle so we don't create that.
        Path(MainWindowUi.PROFILES_DIRECTORY).mkdir(exist_ok=True)
        app = QApplication(sys.argv)
        window = MainWindowUi()
        app.exec_()
    except Exception as e:
        logging.error(e)
