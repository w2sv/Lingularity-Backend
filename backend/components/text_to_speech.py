from io import BytesIO
from typing import List, Optional

from playsound import playsound

from backend.database import MongoDBClient
from backend.ops.google.text_to_speech import GoogleTTSClient
from backend.utils import either_or


_google_tts = GoogleTTSClient()


class TTSClient:
    def __init__(self, language: str):
        super().__init__()

        self._mongodb_client: MongoDBClient = MongoDBClient.instance()

        self.language_variety_choices: Optional[List[str]] = _google_tts.get_variety_choices(language)
        self._language_variety: Optional[str] = self._get_language_variety(language)

        self._playback_speed: float = self._get_playback_speed(self._language_variety)
        self._enabled: bool = self._get_enablement()

        self.audio: Optional[BytesIO] = None

    @property
    def available(self) -> bool:
        return any([self.language_variety_choices, self._language_variety])

    @property
    def employ(self) -> bool:
        return self.available and self.enabled

    # -----------------
    # Language Variety
    # -----------------
    def _get_language_variety(self, language: str) -> Optional[str]:
        """ Returns:
                language if no variety choices available,
                otherwise:
                    variety with enablement being set to True in database if language has already been used,
                    None if not """

        if self.language_variety_choices is None:
            return [None, language][_google_tts.available_for(language)]

        return self._mongodb_client.query_language_variety()

    @property
    def language_variety(self) -> Optional[str]:
        return self._language_variety

    @language_variety.setter
    def language_variety(self, variety: str):
        """ Args:
                variety: element of language_variety_choices, e.g. 'Spanish (Spain)'

            Enters change into database, deletes audio file of old variety """

        # avoid unnecessary database calls
        if variety != self._language_variety:

            # set usage of current variety to False in database if already assigned
            if self._language_variety is not None:
                self._mongodb_client.set_language_variety_usage(self._language_variety, False)

            self._language_variety = variety

            # set usage of new variety to True in database
            self._mongodb_client.set_language_variety_usage(self._language_variety, True)

    # -----------------
    # Enablement
    # -----------------
    def _get_enablement(self) -> bool:
        """ Returns:
                previously stored enablement corresponding to language if existent,
                otherwise fallback of True """

        return either_or(self._mongodb_client.query_tts_enablement(), True)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, enable: bool):
        """ Triggers deletion of audio file if switching from enabled to disabled,
            enters change into database """

        # avoid unnecessary database calls
        if enable != self._enabled:
            self._enabled = enable

            # enter change into database
            self._mongodb_client.set_tts_enablement(self._enabled)

    # -----------------
    # Playback Speed
    # -----------------
    def _get_playback_speed(self, language_variety: Optional[str]) -> float:
        """" Returns:
                previously stored playback speed corresponding to language_variety if existent
                    otherwise fallback of 1.0 """

        if language_variety is not None and (stored_playback_speed := self._mongodb_client.query_playback_speed(language_variety)) is not None:
            return stored_playback_speed
        return 1.0

    @property
    def playback_speed(self) -> Optional[float]:
        return self._playback_speed

    @playback_speed.setter
    def playback_speed(self, value: float):
        assert self._language_variety is not None

        # avoid unnecessary database calls
        if value != self._playback_speed:
            self._playback_speed = value
            self._mongodb_client.set_playback_speed(self._language_variety, self._playback_speed)

    @staticmethod
    def is_valid_playback_speed(playback_speed_input: str) -> bool:
        try:
            return 0.5 <= float(playback_speed_input) <= 2
        except ValueError:
            return False

    # -----------------------
    # Downloading / Playing
    # -----------------------
    def download_audio(self, text: str):
        assert self._language_variety is not None

        self.audio = _google_tts.get_audio(text, self._language_variety)

    def play_audio(self, suspend_for_playback_duration=True):
        """ Suspends program for playback duration, deletes audio file subsequently """

        if self.audio is not None:
            playsound(self.audio.name, block=suspend_for_playback_duration)
            self.audio.close()