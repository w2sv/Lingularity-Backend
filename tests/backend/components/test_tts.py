from time import time

import pytest

from backend.components.tts import TTS


@pytest.mark.parametrize('language, text', [
    ('Italian', 'Ma che fai ?'),
    ('French', "Voulez-vous aller nager ?")
])
def test_text_to_speech(language, text):
    tts = TTS(language)

    tts.download_audio(text=text)

    t1 = time()
    tts.play_audio()
    suspension_duration = time() - t1
    assert suspension_duration > 0.2