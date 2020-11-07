from typing import Set
import os
import subprocess
from itertools import chain

from backend.utils import data, strings
from backend.ops.google import GoogleOp


_IDENTIFIER_DATA_FILE_PATH: str = f'{os.path.dirname(__file__)}/identifiers'


class GoogleTextToSpeech(GoogleOp):
    _LANGUAGE_2_IDENTIFIER = {**data.load_json(_IDENTIFIER_DATA_FILE_PATH), 'Burmese': 'my'}

    def get_audio(self, text: str, language: str, save_path: str, retry=0) -> int:
        if (download_result := subprocess.call(f"curl 'https://translate.google.com/translate_tts?ie=UTF-8&q="
                               f"{'%20'.join(text.split(' '))}&tl={self._get_identifier(language)}&client=tw-ob'"
                               f" -H 'Referer: http://translate.google.com/'"
                               f" -H 'User-Agent: stagefright/1.2 (Linux;Android 5.0)' > "
                               f"{save_path}", stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, shell=True)) != 0 and retry < 5:
            return self.get_audio(text, language, save_path, retry=retry + 1)
        return download_result


AVAILABLE_LANGUAGES: Set[str] = set(chain(*map(lambda language_variation: strings.strip_multiple(language_variation, strings=['(', ')']).split(' '), GoogleTextToSpeech._LANGUAGE_2_IDENTIFIER.keys())))


if __name__ == '__main__':
    tts = GoogleTextToSpeech()
    tts.get_audio('wassupboi', 'it', f'{os.getcwd()}asdf.mp3')
