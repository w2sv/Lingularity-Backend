from typing import Type

from .token_2_comprising_sentence_indices import Token2ComprisingSentenceIndices
from .normalized import (LemmaSentenceIndicesMap, NormalizedToken2SentenceIndicesMap, StemSentenceIndicesMap)
from .unnormalized import Token2SentenceIndicesMap


def get_token_sentence_indices_map(language: str, create=False, load_normalizer=True) -> Token2ComprisingSentenceIndices:
    normalized_maps: list[Type[NormalizedToken2SentenceIndicesMap]] = [LemmaSentenceIndicesMap, StemSentenceIndicesMap]

    for cls in normalized_maps:
        if cls.is_available_for(language):
            if create:
                return cls(None, language, load_normalizer=load_normalizer)
            return cls.load(language)

    if create:
        return Token2SentenceIndicesMap()
    return Token2SentenceIndicesMap.load(language)
