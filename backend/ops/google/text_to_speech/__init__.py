from itertools import chain
import os
from tempfile import NamedTemporaryFile
from typing import Set

from gtts import gTTS

from backend.ops.google import GoogleOperation
from backend.utils import io, strings


_IDENTIFIER_DATA_FILE_PATH: str = f'{os.path.dirname(__file__)}/identifiers'
_LANGUAGE_2_IDENTIFIER = {**io.load_json(_IDENTIFIER_DATA_FILE_PATH), 'Burmese': 'my'}


class GoogleTTSClient(GoogleOperation):
    def __init__(self):
        super().__init__(language_2_identifier=_LANGUAGE_2_IDENTIFIER)

    def get_audio(self, text: str, language: str, domain='com'):
        language_identifier = self._get_identifier(language)
        assert language_identifier is not None

        temp_file = NamedTemporaryFile()
        gTTS(text, lang=language_identifier, lang_check=False, tld=domain).write_to_fp(temp_file)
        return temp_file


AVAILABLE_LANGUAGES: Set[str] = set(
    chain(
        *map(
            lambda language_variation: strings.strip_multiple(
                language_variation,
                strings=['(', ')']
            ).split(' '),
            _LANGUAGE_2_IDENTIFIER.keys()
        )
    )
)
