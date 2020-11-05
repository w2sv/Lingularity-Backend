import os

from backend.trainers.components.text_to_speech import TextToSpeech


def test_text_to_speech():
    tts = TextToSpeech('Italian')

    tts.download_audio_file(text='Z!')
    tts.play_audio()

    assert not os.listdir(tts._AUDIO_FILE_DEPOSIT_DIR)


def test_audio_length_computation():
    assert TextToSpeech._audio_length(f'{os.path.dirname(__file__)}/resources/example_tts_file.mp3') == 2.4
