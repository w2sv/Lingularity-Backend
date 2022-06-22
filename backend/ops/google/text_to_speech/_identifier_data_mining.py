import gtts

from backend.utils import io
from backend.ops.google.text_to_speech import _IDENTIFIER_DATA_FILE_PATH


if __name__ == '__main__':
    data.write_json({v: k for k, v in gtts.tts.tts_langs().items()}, file_path=_IDENTIFIER_DATA_FILE_PATH)
