import pytest

from backend.components.tts._google_client import GoogleTTSClient


@pytest.mark.parametrize('language,language_variety_choices', [
    ('French', {"Canada", "France"}),
    ('Spanish', {"Spain", "Mexico", "United States"}),
    # ('Chinese', ["Chinese (Mandarin/China)", "Chinese (Mandarin/Taiwan)"]),
    ('German', set()),
    ('Portuguese', {"Brazil", "Portugal"}),
    ('Croatian', set())
])
def test_variety_choices(language, language_variety_choices):
    assert set(GoogleTTSClient(language).language_variety_choices) == language_variety_choices


@pytest.mark.parametrize('language,identifier', [
    ('German', 'de'),
    ('Burmese', 'my'),
    ('French', 'fr'),
    ('Sinhala', 'si'),
    ('Vietnamese', 'vi'),
    ('Esperanto', 'eo')
])
def test_get_language_identifier(language, identifier):
    assert GoogleTTSClient._get_identifier(language) == identifier


def test_available_for():
    assert GoogleTTSClient.available_for('Khmer') is True


def test_get_audio():
    audio = GoogleTTSClient('Italian').get_audio('Mamma mia!')

    assert audio.readable()
    assert not audio.closed