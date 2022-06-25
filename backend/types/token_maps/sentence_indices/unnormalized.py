from __future__ import annotations

from backend.types.token_maps.sentence_indices import Token2ComprisingSentenceIndices
from backend.utils.strings import meaningful_types


class Token2SentenceIndicesMap(Token2ComprisingSentenceIndices):
    """ Tokens: punctuation-stripped, proper noun-stripped, digit-free types """

    @staticmethod
    def is_available_for(language: str) -> bool:
        return True

    def best_possibly_normalized_meaningful_types(self, sentence: str) -> set[str]:
        return meaningful_types(sentence, apostrophe_splitting=True)

    # ----------------
    # Query
    # ----------------
    def comprising_sentence_indices(self, vocable: str) -> list[int] | None:
        return self._find_best_fit_sentence_indices(
            relevance_sorted_types=self._length_sorted_meaningful_types(vocable))
