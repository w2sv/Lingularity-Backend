from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Set

from gtts import gTTS, lang

from backend.ops.google import GoogleOperation
from backend.paths import DATA_DIR_PATH
from backend.utils import dictionary, io


_LANGUAGE_2_IETF_TAG = dictionary.reversed(lang.tts_langs())
_LANGUAGE_2_ACCENT_2_TLD: Dict[str, Dict[str, str]] = io.load_json(DATA_DIR_PATH / 'google-tts-accents.json')


class GoogleTTSClient(GoogleOperation):
    AVAILABLE_LANGUAGES: Set[str] = set(_LANGUAGE_2_IETF_TAG.keys())

    def __init__(self):
        super().__init__(language_2_ietf_tag=_LANGUAGE_2_IETF_TAG)

    def get_audio(self, text: str, language: str, variety: Optional[str] = None):
        language_identifier = self._get_identifier(language)
        assert language_identifier is not None

        temp_file = NamedTemporaryFile()

        gTTS(
            text,
            lang=language_identifier,
            lang_check=False,
            tld='com' if variety is None else _LANGUAGE_2_ACCENT_2_TLD[language][variety]
        )\
            .write_to_fp(temp_file)

        return temp_file

    def get_variety_choices(self, query_language: str) -> Optional[List[str]]:
        try:
            return list(_LANGUAGE_2_ACCENT_2_TLD[query_language].keys())
        except KeyError:
            return None