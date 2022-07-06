from __future__ import annotations

from tempfile import _TemporaryFileWrapper, NamedTemporaryFile

from gtts import gTTS, lang
from gtts.tokenizer import Tokenizer

from backend.src.ops.google import GoogleOperationClient
from backend.src.paths import DATA_DIR_PATH
from backend.src.utils import dictionary, io


_LANGUAGE_2_ACCENT_2_TLD: dict[str, dict[str, str]] = io.load_json(DATA_DIR_PATH / 'google-tts-accents.json')


class GoogleTTSClient(GoogleOperationClient):
    _LANGUAGE_2_IETF_TAG = dictionary.items_reversed(lang.tts_langs())
    AVAILABLE_LANGUAGES: set[str] = set(_LANGUAGE_2_IETF_TAG.keys())

    def __init__(self, language: str):
        super().__init__(language)

    def get_audio(self, text: str, accent: str | None = None) -> _TemporaryFileWrapper:
        temp_file = NamedTemporaryFile()

        gTTS(
            text,
            lang=self._language_identifier,
            lang_check=False,
            tld='com' if accent is None else _LANGUAGE_2_ACCENT_2_TLD[self.language][accent],
            pre_processor_funcs=[],
            tokenizer_func=Tokenizer([]).run
        )\
            .write_to_fp(temp_file)

        return temp_file

    def _get_variety_choices(self) -> list[str]:
        try:
            return list(_LANGUAGE_2_ACCENT_2_TLD[self.language])
        except KeyError:
            return list()