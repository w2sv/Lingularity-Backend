from __future__ import annotations

from tempfile import _TemporaryFileWrapper

from playsound import playsound

from backend.src.components.optional_component import OptionalComponent
from backend.src.components.tts._google_client import GoogleTTSClient
from backend.src.database.user_database import LanguageMetadataCollection, UserDatabase
from backend.src.utils import either_or


class TTS(OptionalComponent):
    @staticmethod
    def _available_for(language: str) -> bool:
        return GoogleTTSClient.available_for(language)

    @UserDatabase.receiver
    def __init__(self, language: str, user_database: UserDatabase):
        self._language = language

        self._language_metadata_db_collection: LanguageMetadataCollection = user_database.language_metadata_collection
        self._google_tts_client = GoogleTTSClient(language)

        self._accent: str | None = self._retrieve_previous_accent()

        self._playback_speed: float = self._get_playback_speed(self._accent)  # TODO
        self._enabled: bool = either_or(self._language_metadata_db_collection.query_tts_enablement(), True)

        self._audio: _TemporaryFileWrapper | None = None

    @property
    def _language_identifier(self) -> str:
        return self._language + (self._accent or str())

    @property
    def audio_available(self) -> bool:
        return bool(self._audio)

    # -----------------
    # Language Variety
    # -----------------
    def _retrieve_previous_accent(self) -> str | None:
        if not self._google_tts_client.language_variety_choices:
            return None
        return self._language_metadata_db_collection.query_accent()

    @property
    def accent_choices(self) -> list[str]:
        return self._google_tts_client.language_variety_choices

    @property
    def accent(self) -> str | None:
        return self._accent

    @accent.setter
    def accent(self, new_value: str):
        """ Args:
                new_value: element of language_variety_choices, e.g. 'Spanish (Spain)'

            Enters change into database """

        if new_value != self._accent:
            self._accent = new_value
            self._language_metadata_db_collection.upsert_accent(new_value)

    # -----------------
    # Enablement
    # -----------------
    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, new_value: bool):
        """ Triggers deletion of _audio file if switching from enabled to disabled,
            enters change into database """

        if new_value != self._enabled:
            self._enabled = new_value
            self._language_metadata_db_collection.upsert_tts_enablement(new_value)

    # -----------------
    # Playback Speed
    # -----------------
    def _get_playback_speed(self, accent: str | None) -> float:
        """" Returns:
                previously stored playback speed corresponding to new_value if existent
                    otherwise default of 1.0 """

        DEFAULT_PLAYBACK_SPEED = 1

        if accent and (stored_playback_speed := self._language_metadata_db_collection.query_playback_speed(accent)) is not None:
            return stored_playback_speed
        return DEFAULT_PLAYBACK_SPEED

    @property
    def playback_speed(self) -> float | None:
        return self._playback_speed

    @playback_speed.setter
    def playback_speed(self, value: float):
        if value != self._playback_speed:
            self._playback_speed = value
            self._language_metadata_db_collection.upsert_playback_speed(self._language_identifier, self._playback_speed)

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

        assert self._audio is not None

        playsound(self._audio.name, block=suspend_for_playback_duration)
        self._audio.close()
        self._audio = None
