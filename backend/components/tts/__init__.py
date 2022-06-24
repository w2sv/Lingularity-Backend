from tempfile import _TemporaryFileWrapper
from typing import Optional

from playsound import playsound

from backend.components.tts._google_client import GoogleTTSClient
from backend.database import MongoDBClient
from backend.utils import either_or


class TTS:
    @staticmethod
    def available_for(language: str) -> bool:
        return GoogleTTSClient.available_for(language)

    def __init__(self, language: str):
        super().__init__()

        self._language = language

        self._mongodb_client: MongoDBClient = MongoDBClient.instance()
        self._google_tts_client = GoogleTTSClient(language)

        self._accent: Optional[str] = self._retrieve_previously_set_language_variety()

        self._playback_speed: float = self._get_playback_speed(self._accent)  # TODO
        self._enabled: bool = self._get_enablement()

        self._audio: Optional[_TemporaryFileWrapper] = None

    @property
    def _language_identifier(self) -> str:
        return self._language + (self._accent or str())

    @property
    def audio_playable(self) -> bool:
        return self._audio is not None

    def __getattr__(self, item):
        return getattr(self._google_tts_client, item)

    # -----------------
    # Language Variety
    # -----------------
    def _retrieve_previously_set_language_variety(self) -> Optional[str]:
        if not self._google_tts_client.language_variety_choices:
            return None
        return self._mongodb_client.query_language_variety()

    @property
    def language_variety(self) -> Optional[str]:
        return self._accent

    @language_variety.setter
    def language_variety(self, variety: str):
        """ Args:
                variety: element of language_variety_choices, e.g. 'Spanish (Spain)'

            Enters change into database, deletes _audio file of old accent """

        # avoid unnecessary database calls
        if variety != self._accent:
            self._accent = variety

            # set usage of current accent to False in database if already assigned
            if self._accent is not None:
                self._mongodb_client.set_language_variety_usage(self._accent, False)

            # set usage of new accent to True in database
            self._mongodb_client.set_language_variety_usage(self._accent, True)

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
        """ Triggers deletion of _audio file if switching from enabled to disabled,
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
        # avoid unnecessary database calls
        if value != self._playback_speed:
            self._playback_speed = value
            self._mongodb_client.set_playback_speed(self._language_identifier, self._playback_speed)

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
        self._audio = self._google_tts_client.get_audio(text, self._accent)

    def play_audio(self, suspend_for_playback_duration=True):
        """ Suspends program for playback duration, deletes _audio file subsequently """

        if self._audio is not None:
            playsound(self._audio.name, block=suspend_for_playback_duration)
            self._audio.close()