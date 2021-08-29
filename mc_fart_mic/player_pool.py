from typing import Dict
from collections import deque

from PyQt5.QtMultimedia import QMediaPlayer, QMediaService, QAudioOutputSelectorControl, QMediaContent


AUDIO_OUTPUT_SELECTOR_CONTROL_STRING = "org.qt-project.qt.audiooutputselectorcontrol/5.0"
MIN_MAX_CONCURRENT_SOUNDS: int = 1
MAX_MAX_CONCURRENT_SOUNDS: int = 10


class PlayerPool:
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
        Minimum value is 1 and maximum is 10.
        :raises ValueError: if new_max_concurrent_sounds is out of range
        """
        if not MIN_MAX_CONCURRENT_SOUNDS <= new_max_concurrent_sounds <= MAX_MAX_CONCURRENT_SOUNDS:
            raise ValueError("Max concurrent sounds out of range.")

        difference = new_max_concurrent_sounds - self.max_concurrent_sounds
        if difference > 0:
            self._add_players(difference)
        elif difference < 0:
            self._pop_players(abs(difference))

        self._max_concurrent_sounds = new_max_concurrent_sounds

    @property
    def currently_playing_count(self) -> int:
        return sum(1 for player in self._players if player.state() == QMediaPlayer.State.PlayingState)

    def _add_players(self, number: int):
        """
        Initialize and add number of players to cache.
        We need multiple of them to be able to easily play multiple concurrent sounds.
        """
        for _ in range(number):
            self._players.append(QMediaPlayer())

    def _pop_players(self, number: int):
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

    def available_devices(self) -> Dict[str, str]:
        """
        Get a dict of all available audio output devices.
        :return: Dict where keys are strings representing available audio output device identifier and values represent
        friendly name string of said device identifier. Example:
        {'Default Device': '@device:cm:{E0F118E1-CB14-11D0-BD4E-11A0C900CE97}\\Default Device'}
        """
        # When changing device output the change is propagated across all cached players,
        # so getting available outputs from any of them should always be the same, thus selecting first player
        # as at least one player will exist at all times.
        selector = self._players[0].service().requestControl(AUDIO_OUTPUT_SELECTOR_CONTROL_STRING)
        available_devices = {}
        for device_identifier in selector.availableOutputs():
            friendly_device_name = selector.outputDescription(device_identifier)
            available_devices[friendly_device_name] = device_identifier

        return available_devices

    def change_device(self, device_friendly_name: str):
        """
        Change all cached players to play to specific audio output device based on passed device_friendly_name.
        :param device_friendly_name: str audio device description (friendly name for device identifier)
        :raises ValueError: if device_friendly_name is not one of available devices
        """
        try:
            device_identifier = self.available_devices()[device_friendly_name]
        except KeyError as e:
            raise ValueError(f"Invalid device selected: {e}")

        for player in self._players:
            scv: QMediaService = player.service()
            out: QAudioOutputSelectorControl = scv.requestControl(AUDIO_OUTPUT_SELECTOR_CONTROL_STRING)
            out.setActiveOutput(device_identifier)
            scv.releaseControl(out)

    def stop_all_playbacks(self):
        for player in self._players:
            player.stop()


class PlayerPoolManager:
    """Manages having PLayerPool for multiple devices."""
    def __init__(self, main_player_pool: PlayerPool, additional_player_pool: PlayerPool):
        self._player_pools = (main_player_pool, additional_player_pool)

    @property
    def main_player_pool(self) -> PlayerPool:
        return self._player_pools[0]

    @property
    def additional_player_pool(self) -> PlayerPool:
        return self._player_pools[1]

    def play(self, *, url: str, also_play_on_additional: bool):
        main_content = QMediaContent(url)
        main_player = self.main_player_pool.get_player()
        main_player.setMedia(main_content)
        main_player.play()

        additional_content = QMediaContent(url)
        additional_player = self.additional_player_pool.get_player()
        additional_player.setMedia(additional_content)

        main_player.play()
        if also_play_on_additional:
            additional_player.play()

    def stop_all_playback(self):
        for player_pool in self._player_pools:
            player_pool.stop_all_playbacks()

    def set_max_concurrent_sounds(self, max_concurrent_sounds: int):
        for player_pool in self._player_pools:
            player_pool.max_concurrent_sounds = max_concurrent_sounds
