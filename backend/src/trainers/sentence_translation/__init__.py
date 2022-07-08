from __future__ import annotations

from backend.src.trainers.trainer_backend import TrainerBackend
from backend.src.components.tts import TTS
from backend.src.trainers.sentence_translation import modes
from backend.src.types.bilingual_corpus import BilingualCorpus, SentencePair


class SentenceTranslationTrainerBackend(TrainerBackend[SentencePair, BilingualCorpus]):
    def __init__(self, non_english_language: str, train_english: bool):
        super().__init__(non_english_language, train_english)

        self._non_english_language = non_english_language

        self.tts: TTS | None = TTS.get_if_available_for(self.language)
        self.sentence_data_filter: modes.SentenceDataFilter = None  # type: ignore

    @property
    def tts_available(self) -> bool:
        return self.tts is not None

    def set_item_iterator(self):
        # get sentence data
        bilingual_corpus = self._get_bilingual_corpus()

        # get mode filtered sentence data
        filtered_sentence_data = self.sentence_data_filter(bilingual_corpus, self._non_english_language)

        self._set_item_iterator(items=filtered_sentence_data)
