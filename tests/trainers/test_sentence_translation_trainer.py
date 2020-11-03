from backend.trainers.sentence_translation import SentenceTranslationTrainerBackend
from backend.trainers.sentence_translation import modes


def test_sentence_translation_trainer():
    backend = SentenceTranslationTrainerBackend('Italian', train_english=False)
    backend.sentence_data_filter = modes.diction_expansion.filter_sentence_data
    backend.set_item_iterator()

    for _ in range(100):
        assert backend.get_training_item() is not None
