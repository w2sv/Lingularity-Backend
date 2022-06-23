from time import time

from backend.components.tts import TTS


def test_text_to_speech():
    tts = TTS('Italian')

    tts.download_audio(text="Ma?")

    t1 = time()
    tts.play_audio()
    suspension_duration = time() - t1
    assert suspension_duration > 0.2