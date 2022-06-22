from .base import SegmentSentenceIndicesMap
from .normalized import (LemmaSentenceIndicesMap, NormalizedTokenSentenceIndicesMap, StemSentenceIndicesMap)
from .unnormalized import TokenSentenceIndicesMap


def get_token_sentence_indices_map(language: str, create=False, load_normalizer=True) -> SegmentSentenceIndicesMap:
    for cls in [LemmaSentenceIndicesMap, StemSentenceIndicesMap]:
        if cls.is_available(language):  # type: ignore
            return cls(language, create=create, load_normalizer=load_normalizer)

    return TokenSentenceIndicesMap(language, create=create)
