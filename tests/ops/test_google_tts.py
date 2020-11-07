import pytest

from backend.ops.google.text_to_speech import GoogleTextToSpeech


google_tts = GoogleTextToSpeech()


@pytest.mark.parametrize('language,variety_choices', [
    ('French', ["French (Canada)", "French (France)"]),
    ('Spanish', ["Spanish (Spain)", "Spanish (United States)"]),
    ('Chinese', ["Chinese (Mandarin/China)", "Chinese (Mandarin/Taiwan)"]),
    ('German', None),
    ('Portuguese', ["Portuguese (Brazil)", "Portuguese (Portugal)"]),
    ('Croatian', None)
])
def test_variety_choices(language, variety_choices):
    assert google_tts.get_variety_choices(language) == variety_choices


@pytest.mark.parametrize('language,identifier', [
    ('German', 'de'),
    ('Burmese', 'my'),
    ('French', 'fr'),
    ('Sinhala', 'si'),
    ('Vietnamese', 'vi'),
    ('Esperanto', 'eo')
])
def test_get_language_identifier(language, identifier):
    assert google_tts._get_identifier(language) == identifier


def test_available_for():
    assert google_tts.available_for('Khmer') is True
