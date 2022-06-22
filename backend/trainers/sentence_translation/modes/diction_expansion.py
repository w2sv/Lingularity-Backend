from itertools import chain
from typing import *

from backend.components import SentenceData
from backend.components.mappings.token import get_token_maps


def filter_sentence_data(sentence_data: SentenceData, language: str) -> SentenceData:
    sentence_indices_map, occurrences_map = get_token_maps(language)

    tokens: Iterator[str] = (token for token, n_occurrences in occurrences_map.items() if n_occurrences <= occurrences_map.occurrence_mean)
    return sentence_data[list(set(chain.from_iterable(map(sentence_indices_map.__getitem__, tokens))))]
