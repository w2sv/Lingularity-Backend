from pathlib import Path

import pytest

from backend.ops.google.text_to_speech import GoogleTTSClient


@pytest.fixture(scope='module')
def google_tts_client() -> GoogleTTSClient:
    return GoogleTTSClient()


@pytest.mark.parametrize('language,variety_choices', [
    ('French', ["French (Canada)", "French (France)"]),
    ('Spanish', ["Spanish (Spain)", "Spanish (United States)"]),
    ('Chinese', ["Chinese (Mandarin/China)", "Chinese (Mandarin/Taiwan)"]),
    ('German', None),
    ('Portuguese', ["Portuguese (Brazil)", "Portuguese (Portugal)"]),
    ('Croatian', None)
])
def test_variety_choices(language, variety_choices, google_tts_client):
    assert google_tts_client.get_variety_choices(language) == variety_choices


@pytest.mark.parametrize('language,identifier', [
    ('German', 'de'),
    ('Burmese', 'my'),
    ('French', 'fr'),
    ('Sinhala', 'si'),
    ('Vietnamese', 'vi'),
    ('Esperanto', 'eo')
])
def test_get_language_identifier(language, identifier, google_tts_client):
    assert google_tts_client._get_identifier(language) == identifier


def test_available_for(google_tts_client):
    assert google_tts_client.available_for('Khmer') is True


_temp_file_path = Path(__file__).parent/'temp.mp3'


def test_get_audio(google_tts_client):
    google_tts_client.get_audio('Mamma mia!', language='Italian', save_path=_temp_file_path)

    assert _temp_file_path.exists()
    assert _temp_file_path.stat().st_size != 0


@pytest.fixture(autouse=True)
def cleanup():
    yield
    _temp_file_path.unlink(missing_ok=True)