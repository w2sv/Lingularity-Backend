from backend.trainers.components.text_to_speech import TextToSpeech


def test_text_to_speech():
    tts = TextToSpeech('Italian')
    tts.download_audio_file(text='p')
    tts.play_audio()
