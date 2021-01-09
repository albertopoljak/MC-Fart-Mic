from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, qApp, QStyle

from config import Config
from player_pool import PlayerPool
from message_boxes import show_simple_info_message


class SettingsUi(QWidget):
    def __init__(self):
        super(SettingsUi, self).__init__()
        uic.loadUi("layouts/settings.ui", self)
        self.setFixedSize(self.size())

        all_options = PlayerPool().available_devices()

        self.test_virtual_device.setIcon(qApp.style().standardIcon(QStyle.SP_MediaVolume))
        self.combo_box_virtual_device.addItems(all_options)
        self.combo_box_virtual_device.currentTextChanged.connect(self.on_virtual_device_combobox_changed)
        self.help_virtual_audio_device.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_virtual_audio_device.clicked.connect(self.show_help_virtual_audio_device)

        self.label_max_concurrent_sounds_value.setText(str(self._slider_meta_value()))
        self.slider_max_concurrent_sounds.valueChanged.connect(self.slider_max_concurrent_sounds_changed)
        self.help_max_concurrent_sounds.setIcon(qApp.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.help_max_concurrent_sounds.clicked.connect(self.show_help_max_concurrent_sounds)

        # Load states from previous run
        Config.register_combobox(self.combo_box_virtual_device)
        Config.register_slider(self.slider_max_concurrent_sounds)
        PlayerPool().max_concurrent_sounds = int(self.slider_max_concurrent_sounds.value())
        Config.register_checkbox(self.check_minimize_to_tray)
        Config.register_checkbox(self.check_show_try_msg_on_minimize)
        Config.register_checkbox(self.check_minimize_on_close)

    @pyqtSlot(str)
    def on_virtual_device_combobox_changed(self, value):
        PlayerPool().change_device(value)

    def _slider_meta_value(self) -> int:
        """
        Instead of getting raw slider value get the value that current slider represents (the two might not be the same
        example slider value 0-100 while our meta value is 0-10).
        This is dynamic and is made so it's easy to change ranges in the future.
        """
        slider_range = self.slider_max_concurrent_sounds.maximum() - self.slider_max_concurrent_sounds.minimum()
        value_rage = PlayerPool.MAX_MAX_CONCURRENT_SOUNDS - PlayerPool.MIN_MAX_CONCURRENT_SOUNDS
        step_value = (self.slider_max_concurrent_sounds.value() - 1) / slider_range
        return int(PlayerPool.MIN_MAX_CONCURRENT_SOUNDS + value_rage * step_value)

    @pyqtSlot()
    def slider_max_concurrent_sounds_changed(self):
        new_value = self._slider_meta_value()
        self.label_max_concurrent_sounds_value.setText(str(new_value))
        PlayerPool().max_concurrent_sounds = new_value

    @pyqtSlot()
    def show_help_virtual_audio_device(self):
        show_simple_info_message(
            "Select virtual audio device here.\n"
            "This device should pass all sound it gets back to your microphone.\n\n"
            "Click on Application/Help menu if you don't know what virtual audio device is."
        )

    @pyqtSlot()
    def show_help_max_concurrent_sounds(self):
        show_simple_info_message(
            "Maximum number of sounds that can play at the same time.\n\n"
            "Once this limit is exceeded the oldest currently playing sound will stop playing "
            "and new sound will play instead."
        )
