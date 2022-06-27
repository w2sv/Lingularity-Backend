from __future__ import annotations

from backend.trainers.base import TrainerBackend
from backend.components.tts import TTS
from backend.trainers.sentence_translation import modes
from backend.types.bilingual_corpus import BilingualCorpus, SentencePair


class SentenceTranslationTrainerBackend(TrainerBackend[SentencePair, BilingualCorpus]):
    def __init__(self, non_english_language: str, train_english: bool):
        super().__init__(non_english_language, train_english)

        self.tts: TTS | None = TTS(self.language) if TTS.available_for(self.language) else None
        self._sentence_data_filter: modes.SentenceDataFilter = None  # type: ignore

    @property
    def tts_available(self) -> bool:
        return self.tts is not None

    @property
    def sentence_data_filter(self) -> modes.SentenceDataFilter:
        return self._sentence_data_filter

    @sentence_data_filter.setter
    def sentence_data_filter(self, _filter: modes.SentenceDataFilter):
        self._sentence_data_filter = _filter

    def set_item_iterator(self):
        # get sentence data
        sentence_data = self._get_sentence_data()

        # get mode filtered sentence data
        filtered_sentence_data = self._sentence_data_filter(sentence_data, self._non_english_language)

        self._set_item_iterator(items=filtered_sentence_data)
