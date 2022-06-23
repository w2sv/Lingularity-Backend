from time import time

from backend.components.text_to_speech import TTSClient
from tests.config import instantiate_database


def test_text_to_speech():
    tts = TTSClient('Italian')

    tts.download_audio(text="Ma?")

    t1 = time()
    tts.play_audio()
    suspension_duration = time() - t1
    assert suspension_duration > 0.2