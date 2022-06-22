import gtts

from backend.ops.google.text_to_speech import _IDENTIFIER_DATA_FILE_PATH
from backend.utils import io


if __name__ == '__main__':
    # TODO
    io.write_json({v: k for k, v in gtts.tts.tts_langs().items()}, file_path=_IDENTIFIER_DATA_FILE_PATH)
