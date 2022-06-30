from .occurrences import TokenOccurrencesMap
from .sentence_indices import (
    get_token_sentence_indices_map,
    Token2ComprisingSentenceIndices
)


def get_token_maps(language: str) -> tuple[Token2ComprisingSentenceIndices, TokenOccurrencesMap]:
    return get_token_sentence_indices_map(language, load_normalizer=False), TokenOccurrencesMap.load(language)
