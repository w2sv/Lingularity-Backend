import pytest

from backend.src.trainers.sentence_translation import modes, SentenceTranslationTrainerBackend


@pytest.mark.parametrize('language, train_english, tts_available, sentence_data_filter, n_traverse_sentences', [
    (
        'Galician', False, False, modes.random.filter_sentence_data, 30
    ),
    (
        'Bulgarian', False, True, modes.diction_expansion.filter_sentence_data, 70
    ),
    (
        'Arabic', False, True, modes.simple.filter_sentence_data, 130
    ),
    (
        'Assamese', True, True, modes.simple.filter_sentence_data, 130
    ),
])
def test_sentence_translation_trainer(language, train_english, tts_available, sentence_data_filter, n_traverse_sentences):
    backend = SentenceTranslationTrainerBackend(language, train_english=train_english)
    assert tts_available == backend.tts_available
    assert str(backend) == 's'

    backend.sentence_data_filter = sentence_data_filter
    backend.set_item_iterator()

    for _ in range(n_traverse_sentences):
        assert backend.get_training_item() is not None
