from backend.trainers.sentence_translation import modes, SentenceTranslationTrainerBackend


def test_sentence_translation_trainer():
    backend = SentenceTranslationTrainerBackend('Galician', train_english=False)
    backend.sentence_data_filter = modes.random.filter_sentence_data
    backend.set_item_iterator()

    for _ in range(150):
        assert backend.get_training_item() is not None
    assert backend.get_training_item() is None
