from tempfile import _TemporaryFileWrapper, NamedTemporaryFile
from typing import Dict, List, Optional, Set

from gtts import gTTS, lang

from backend.ops.google import GoogleOperation
from backend.data_paths import DATA_DIR_PATH
from backend.utils import dictionary, io


_LANGUAGE_2_ACCENT_2_TLD: Dict[str, Dict[str, str]] = io.load_json(DATA_DIR_PATH / 'google-tts-accents.json')


class GoogleTTSClient(GoogleOperation):
    _LANGUAGE_2_IETF_TAG = dictionary.reversed(lang.tts_langs())
    AVAILABLE_LANGUAGES: Set[str] = set(_LANGUAGE_2_IETF_TAG.keys())

    def __init__(self, language: str):
        super().__init__(language)

    def get_audio(self, text: str, accent: Optional[str] = None) -> _TemporaryFileWrapper:
        language_identifier = self._get_identifier(self.language)
        assert language_identifier is not None

        temp_file = NamedTemporaryFile()

        gTTS(
            text,
            lang=language_identifier,
            lang_check=False,
            tld='com' if accent is None else _LANGUAGE_2_ACCENT_2_TLD[self.language][accent]
        )\
            .write_to_fp(temp_file)

        return temp_file

    def _get_variety_choices(self) -> List[str]:
        try:
            return list(_LANGUAGE_2_ACCENT_2_TLD[self.language].keys())
        except KeyError:
            return list()