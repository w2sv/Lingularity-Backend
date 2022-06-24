from typing import List, Optional

from backend.types.token_maps.sentence_indices import SegmentSentenceIndicesMap
from backend.utils.strings import get_meaningful_tokens


class TokenSentenceIndicesMap(SegmentSentenceIndicesMap):
    """ keys: punctuation-stripped, proper noun-stripped, digit-free tokens """

    def __init__(self, language: str, create=False):
        super().__init__(language, create=create)

    def tokenize(self, sentence: str) -> List[str]:
        return get_meaningful_tokens(sentence, apostrophe_splitting=True)

    # ----------------
    # Query
    # ----------------
    def query_sentence_indices(self, vocable_entry: str) -> Optional[List[int]]:
        return self._find_best_fit_sentence_indices(relevance_sorted_tokens=self._get_length_sorted_meaningful_tokens(vocable_entry))
