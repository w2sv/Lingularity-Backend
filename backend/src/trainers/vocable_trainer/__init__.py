from collections import defaultdict
from itertools import tee
from typing import Iterable, Iterator

import numpy as np

from backend.src.trainers.trainer_backend import TrainerBackend
from backend.src.types.bilingual_corpus import BilingualCorpus
from backend.src.types.token_maps import get_token_sentence_indices_map, Token2ComprisingSentenceIndices
from backend.src.types.vocable_entry import is_perfected, VocableEntries, VocableEntry


class VocableTrainerBackend(TrainerBackend[VocableEntry, VocableEntries]):
    def __init__(self, non_english_language: str, train_english: bool):
        super().__init__(non_english_language, train_english)

        self._sentence_data: BilingualCorpus = self._get_sentence_data()
        self._token_2_sentence_indices: Token2ComprisingSentenceIndices = get_token_sentence_indices_map(self.language, load_normalizer=True)

        self.paraphrases: dict[str, list[str]] = None  # type: ignore
        self.new_vocable_entries: VocableEntries = []

    @property
    def new_vocable_entries_available(self) -> bool:
        return bool(self.new_vocable_entries)

    # ---------------
    # Pre Training
    # ---------------
    def set_item_iterator(self):
        """ Additionally sets paraphrases, new_vocable_entries iterator """

        vocable_entries_to_be_trained = list(self._vocable_entries_to_be_trained())

        self.paraphrases = self._find_paraphrases(vocable_entries_to_be_trained)
        self.new_vocable_entries = list(filter(lambda entry: entry.is_new, vocable_entries_to_be_trained))
        self._set_item_iterator(vocable_entries_to_be_trained)

    def _vocable_entries_to_be_trained(self) -> Iterator[VocableEntry]:
        return filter(
                is_perfected,
                self.user_database.vocabulary_collection.entries()
            )

    @staticmethod
    def _find_paraphrases(vocable_entries: Iterable[VocableEntry]) -> dict[str, list[str]]:
        """ Returns:
                Dict[english_meaning: [synonym_1, synonym_2, ..., synonym_n]]

                for n >= 2 paraphrases contained within retrieved vocable entries possessing the IDENTICAL
                english the-stripped meaning"""

        meaning_2_vocables = defaultdict(list)

        for entry in vocable_entries:
            meaning_2_vocables[entry.the_stripped_meaning].append(entry.vocable)

        return {meaning: synonyms for meaning, synonyms in meaning_2_vocables.items() if len(synonyms) >= 2}

    # ---------------
    # Training
    # ---------------
    def related_sentence_pairs(self, entry: str, n: int) -> list[tuple[str, str]]:
        if (sentence_indices := self._token_2_sentence_indices.comprising_sentence_indices(entry)) is None:
            return []

        nd_sentence_indices = np.asarray(sentence_indices)
        np.random.shuffle(nd_sentence_indices)

        assert nd_sentence_indices is not None

        return self._sentence_data[nd_sentence_indices[:n]].tolist()
