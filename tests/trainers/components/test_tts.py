from backend.trainers.components.text_to_speech import TextToSpeech


def test_text_to_speech():
    tts = TextToSpeech('Italian')

    tts.download_audio_file(text='Z!')
    tts.download_audio_file(text='Z!')
    tts.download_audio_file(text='Il passagio non ritorna mai')

    assert tts._audio_length == 2.4

    tts.play_audio()
