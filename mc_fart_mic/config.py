import json
import logging
from pathlib import Path
from functools import partial
from typing import Any, Callable

from PyQt5 import QtCore
from PyQt5.QtWidgets import QCheckBox, QSlider, QComboBox


logger = logging.getLogger(__name__)


class Config:
    """
    Class dealing with saving and reloading the options state when program is opened again.

    You just need to call appropriate classmethod for your object and that's it.
    In the backend the classmethod will tie appropriate update method of that object and for each object state update
    save that new state change to config file.

    This classmethod will also restore object state when register method is called,
    if such object is found in saved config file.

    """
    PATH = Path("config.json")

    try:
        with open(PATH) as f:
            _config_data = json.load(f)
    except FileNotFoundError:
        logger.info("Can't find config file, creating new empty one.")
        open(PATH, "w").close()
        _config_data = {}
    except Exception as e:  # noqa PyBroadException
        logger.warning(f"Can't open config file: {e}, treating it as if it's empty.")
        _config_data = {}

    @classmethod
    def register_combobox(cls, combobox: QComboBox):
        if combobox.objectName() in cls._config_data:
            value = cls._config_data[combobox.objectName()]
            item_index = combobox.findText(value, QtCore.Qt.MatchFixedString)
            if item_index >= 0:
                combobox.setCurrentIndex(item_index)

        action = partial(cls._config_data_update, combobox.objectName, combobox.currentText)
        combobox.currentTextChanged.connect(lambda _: action())

    @classmethod
    def register_checkbox(cls, checkbox: QCheckBox):
        if checkbox.objectName() in cls._config_data:
            checkbox.setChecked(cls._config_data[checkbox.objectName()])

        action = partial(cls._config_data_update, checkbox.objectName, checkbox.isChecked)
        checkbox.stateChanged.connect(lambda _: action())

    @classmethod
    def register_slider(cls, slider: QSlider):
        if slider.objectName() in cls._config_data:
            slider.setValue(cls._config_data[slider.objectName()])

        action = partial(cls._config_data_update, slider.objectName, slider.value)
        slider.valueChanged.connect(lambda _: action())

    @classmethod
    def _config_data_update(cls, key_callable: Callable[[], str], value_callable: Callable[[], Any]):
        """
        Update config values in memory and, since we updated, save them to config file.

        :param key_callable: Callable that takes no arguments and when called should return a string
                             representing nameID of object.
        :param value_callable: Callable that takes no arguments and when called should return some value that
                               represent new set value for object tied to key_callable.
        """
        key, value = key_callable(), value_callable()
        cls._config_data[key] = value
        with open(cls.PATH, "w") as f:
            try:
                json.dump(cls._config_data, f, indent=4)
            except Exception as e:  # noqa PyBroadException
                logger.error(f"Can't save config: {e}")
