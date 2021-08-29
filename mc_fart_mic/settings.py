from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, qApp, QStyle

from config import Config
from message_boxes import show_simple_info_message
from player_pool import PlayerPoolManager, MIN_MAX_CONCURRENT_SOUNDS, MAX_MAX_CONCURRENT_SOUNDS


class SettingsUi(QWidget):
    def __init__(self, player_pool_manager: PlayerPoolManager):
        super(SettingsUi, self).__init__()
        uic.loadUi("layouts/settings.ui", self)
        self.setFixedSize(self.size())

        self._player_pool_manager_ref = player_pool_manager

        self.combo_box_virtual_device.addItems(self._player_pool_manager_ref.main_player_pool.available_devices())
        self.combo_box_virtual_device.currentTextChanged.connect(self.on_virtual_device_combobox_changed)
        self.help_virtual_audio_device.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_virtual_audio_device.clicked.connect(self.show_help_virtual_audio_device)

        self.check_enable_additional_playback_device.stateChanged.connect(self.check_enable_additional_playback_device_changed)
        self.combo_box_additional_playback_device.addItems(self._player_pool_manager_ref.additional_player_pool.available_devices())
        self.combo_box_additional_playback_device.currentTextChanged.connect(self.on_additional_playback_device_combobox_changed)
        self.help_additional_playback_device.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_additional_playback_device.clicked.connect(self.show_help_additional_playback_device)

        self.label_max_concurrent_sounds_value.setText(str(self._slider_meta_value()))
        self.slider_max_concurrent_sounds.valueChanged.connect(self.slider_max_concurrent_sounds_changed)
        self.help_max_concurrent_sounds.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_max_concurrent_sounds.clicked.connect(self.show_help_max_concurrent_sounds)

        # self.label_max_keyword_length_value.setText(str(self._slider_meta_value()))
        self.slider_max_keyword_length.valueChanged.connect(self.slider_max_keyword_length_changed)
        self.help_maximum_keyword_length.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_maximum_keyword_length.clicked.connect(self.show_help_maximum_keyword_length)

        # Load states from previous run
        Config.register_combobox(self.combo_box_virtual_device)
        Config.register_checkbox(self.check_enable_additional_playback_device)
        Config.register_combobox(self.combo_box_additional_playback_device)
        Config.register_slider(self.slider_max_concurrent_sounds)
        self._player_pool_manager_ref.set_max_concurrent_sounds(int(self.slider_max_concurrent_sounds.value()))
        Config.register_slider(self.slider_max_keyword_length)
        # todo add values based on above
        Config.register_checkbox(self.check_minimize_to_tray)
        Config.register_checkbox(self.check_show_try_msg_on_minimize)
        Config.register_checkbox(self.check_minimize_on_close)

    @pyqtSlot(str)
    def on_virtual_device_combobox_changed(self, value: str):
        self._player_pool_manager_ref.main_player_pool.change_device(value)

    @pyqtSlot(int)
    def check_enable_additional_playback_device_changed(self, _value: int):
        if self.check_enable_additional_playback_device.isChecked():
            self.combo_box_additional_playback_device.setEnabled(True)
        else:
            self.combo_box_additional_playback_device.setEnabled(False)

    @pyqtSlot(str)
    def on_additional_playback_device_combobox_changed(self, value: str):
        self._player_pool_manager_ref.additional_player_pool.change_device(value)

    def _slider_meta_value(self) -> int:
        """
        Instead of getting raw slider value get the value that current slider represents (the two might not be the same
        example slider value 0-100 while our meta value is 0-10).
        This is dynamic and is made so it's easy to change ranges in the future.
        """
        slider_range = self.slider_max_concurrent_sounds.maximum() - self.slider_max_concurrent_sounds.minimum()
        value_rage = MAX_MAX_CONCURRENT_SOUNDS - MIN_MAX_CONCURRENT_SOUNDS
        step_value = (self.slider_max_concurrent_sounds.value() - 1) / slider_range
        return int(MIN_MAX_CONCURRENT_SOUNDS + value_rage * step_value)

    @pyqtSlot()
    def slider_max_concurrent_sounds_changed(self):
        new_value = self._slider_meta_value()
        self.label_max_concurrent_sounds_value.setText(str(new_value))
        self._player_pool_manager_ref.set_max_concurrent_sounds(new_value)

    @pyqtSlot()
    def slider_max_keyword_length_changed(self):
        new_value = self._slider_meta_value()
        self.label_max_keyword_length_value.setText(str(new_value))
        raise NotImplemented()

    @pyqtSlot()
    def show_help_virtual_audio_device(self):
        show_simple_info_message(
            "Select virtual audio device here.\n"
            "This device should pass all sound it gets back to your microphone.\n\n"
            "Click on Application/Help menu if you don't know what virtual audio device is."
        )

    @pyqtSlot()
    def show_help_additional_playback_device(self):
        show_simple_info_message(
            "Select additional audio playback device.\n"
            "If, for whatever reason, you want the playing sounds to be outputted to additional device aside from"
            "virtual device you can select one here.\n\n"
            "You need to enable it in the checkbox."
        )

    @pyqtSlot()
    def show_help_max_concurrent_sounds(self):
        show_simple_info_message(
            "Maximum number of sounds that can play at the same time.\n\n"
            "Once this limit is exceeded the oldest currently playing sound will stop playing "
            "and new sound will play instead."
        )

    @pyqtSlot()
    def show_help_maximum_keyword_length(self):
        show_simple_info_message(
            "Number of last characters typed that the program will save in memory.\n\n"
            "These are then used to trigger playing by typed keywords, as opposed to playing by hotkey.\n\n"
            "For example if you type DESPACITO it can trigger playing despacito file if it's set with that keyword.\n\n"
            "Setting this value to 0 will disable this feature."
        )
