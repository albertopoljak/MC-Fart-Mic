from typing import List
from collections import deque

from PyQt5.QtMultimedia import QMediaPlayer, QMediaService, QAudioOutputSelectorControl


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PlayerPool(metaclass=Singleton):
    AUDIO_OUTPUT_SELECTOR_CONTROL_STRING = "org.qt-project.qt.audiooutputselectorcontrol/5.0"
    MIN_MAX_CONCURRENT_SOUNDS: int = 1
    MAX_MAX_CONCURRENT_SOUNDS: int = 10

    def __init__(self, max_concurrent_sounds: int = 3):
        self._max_concurrent_sounds = self.max_concurrent_sounds = max_concurrent_sounds
        self._players = deque()
        self._add_players(self.max_concurrent_sounds)

    @property
    def max_concurrent_sounds(self) -> int:
        """
        Returns how many concurrent sounds can play at the same time.
        :return: int max_concurrent_sounds
        """
        return self._max_concurrent_sounds

    @max_concurrent_sounds.setter
    def max_concurrent_sounds(self, new_max_concurrent_sounds: int):
        """
        Set how many concurrent sounds can play at the same time.
        Minimum value is 0 and maximum is 10.
        :raises ValueError: if new_max_concurrent_sounds is out of range
        """
        if not self.MIN_MAX_CONCURRENT_SOUNDS <= new_max_concurrent_sounds <= self.MAX_MAX_CONCURRENT_SOUNDS:
            raise ValueError("Max concurrent sounds out of range.")

        difference = new_max_concurrent_sounds - self.max_concurrent_sounds
        if difference > 0:
            self._add_players(difference)
        elif difference < 0:
            self._remove_players(abs(difference))

        self._max_concurrent_sounds = new_max_concurrent_sounds

    def _add_players(self, number: int):
        """
        Initialize and add number of players to cache.
        We need multiple of them to be able to easily play multiple concurrent sounds.
        """
        for _ in range(number):
            self._players.append(QMediaPlayer())

    def _remove_players(self, number: int):
        """Remove number of players from cache."""
        for _ in range(number):
            self._players.pop()

    def get_player(self) -> QMediaPlayer:
        """
        Returns first available player that isn't playing currently or, if all are playing,
        returns the oldest player (that is playing for longest).
        :return: QMediaPlayer
        """
        for player in self._players:
            if player.state() == QMediaPlayer.State.StoppedState:
                return player

        oldest = sorted(self._players, key=lambda _player: _player.duration() - _player.position(), reverse=True)[0]
        return oldest

    def available_devices(self) -> List[str]:
        """
        Get a list of all available audio output devices.
        :return: list of strings where each string represent available audio output device identifier.
        """
        # When changing device output the change is propagated across all cached players,
        # so getting available outputs from any of them should always be the same.
        return self._players[0].service().requestControl(self.AUDIO_OUTPUT_SELECTOR_CONTROL_STRING).availableOutputs()

    def change_device(self, device_identifier: str):
        """
        Change all cached players to play to specific audio output device based on passed device_identifier.
        :param device_identifier: str audio device identifier
        :raises ValueError: if device_identifier is not one of available devices
        """
        if device_identifier not in self.available_devices():
            raise ValueError("Invalid device identifier.")

        for player in self._players:
            scv: QMediaService = player.service()
            out: QAudioOutputSelectorControl = scv.requestControl(self.AUDIO_OUTPUT_SELECTOR_CONTROL_STRING)
            out.setActiveOutput(device_identifier)
            scv.releaseControl(out)

    def stop_all_playbacks(self):
        for player in self._players:
            player.stop()
