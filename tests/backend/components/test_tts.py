from time import time

import pytest

from backend.src.components.tts import GoogleTTSClient, TTS


@pytest.mark.parametrize('language, text', [
    ('Italian', 'Ma che fai ?'),
    ('French', "Voulez-vous aller nager ?"),
    ('Italian', 'Macche?')
])
def test_text_to_speech(language, text):
    tts = TTS(language)

    tts.download_audio(text=text)

    t1 = time()
    tts.play_audio()
    suspension_duration = time() - t1
    assert suspension_duration > 0.2


@pytest.mark.parametrize('accent', [
    'Brazil',
    'Portugal'
])
def test_download_audio_with_accent(accent):
    tts = TTS('Portuguese')
    tts._accent = accent

    tts.download_audio('O que voce faz?')


class TestGoogleTTS:
    @pytest.mark.parametrize('language,language_variety_choices', [
        ('French', {"Canada", "France"}),
        ('Spanish', {"Spain", "Mexico", "United States"}),
        # ('Chinese', ["Chinese (Mandarin/China)", "Chinese (Mandarin/Taiwan)"]),
        ('German', set()),
        ('Portuguese', {"Brazil", "Portugal"}),
        ('Croatian', set())
    ])
    def test_variety_choices(self, language, language_variety_choices):
        assert set(GoogleTTSClient(language).language_variety_choices) == language_variety_choices

    @pytest.mark.parametrize('language,identifier', [
        ('German', 'de'),
        ('Burmese', 'my'),
        ('French', 'fr'),
        ('Sinhala', 'si'),
        ('Vietnamese', 'vi'),
        ('Esperanto', 'eo'),
        ('Chinese', 'zh-CN'),
        ('Mandarin', 'zh-TW')
    ])
    def test_get_language_identifier(self, language, identifier):
        assert GoogleTTSClient._get_identifier(language) == identifier

    @pytest.mark.parametrize('language, expected', [
        ('Khmer', True),
        ('Mandarin', True),
        ('Chinese', True),
        ('Sächsch', False)
    ])
    def test_available_for(self, language, expected):
        assert GoogleTTSClient.available_for(language) == expected

    def test_get_audio(self):
        audio = GoogleTTSClient('Italian').download_audio('Mamma mia!')

        assert audio.readable()
        assert not audio.closed