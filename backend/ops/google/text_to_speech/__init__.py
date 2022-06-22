from typing import Set
import os
import subprocess
from itertools import chain

from backend.utils import io, strings
from backend.ops.google import GoogleOp
from backend.ops.google.text_to_speech import gtts


_IDENTIFIER_DATA_FILE_PATH: str = f'{os.path.dirname(__file__)}/identifiers'


class GoogleTextToSpeech(GoogleOp):
    _LANGUAGE_2_IDENTIFIER = {**data.load_json(_IDENTIFIER_DATA_FILE_PATH), 'Burmese': 'my'}

    def get_audio_curled(self, text: str, language: str, save_path: str):
        subprocess.call(
                f"curl 'https://translate.google.com/translate_tts?ie=UTF-8"
                f"&q={'%20'.join(text.split(' '))}"
                f"&tl={self._get_identifier(language)}"
                f"&client=tw-ob'"
                f" -H 'Referer: http://translate.google.com/'"
                f" -H 'User-Agent: stagefright/1.2 (Linux;Android 5.0)' > "
                f"{save_path}", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)

    def get_audio(self, text: str, language: str, save_path: str):
        language_identifier = self._get_identifier(language)
        assert language_identifier is not None

        gtts.get_audio(text=text, language_identifier=language_identifier, save_path=save_path)


AVAILABLE_LANGUAGES: Set[str] = set(chain(*map(lambda language_variation: strings.strip_multiple(language_variation, strings=['(', ')']).split(' '), GoogleTextToSpeech._LANGUAGE_2_IDENTIFIER.keys())))


if __name__ == '__main__':
    tts = GoogleTextToSpeech()
    tts.get_audio('wassupboi', 'Italian', f'{os.getcwd()}test.mp3')
