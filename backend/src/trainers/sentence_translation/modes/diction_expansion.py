from itertools import chain
from typing import Iterator

from backend.src.types.bilingual_corpus import BilingualCorpus
from backend.src.types.token_maps import get_token_maps


def filter_sentence_data(sentence_data: BilingualCorpus, non_english_language: str) -> BilingualCorpus:
    sentence_indices_map, occurrences_map = get_token_maps(non_english_language)

    tokens: Iterator[str] = (token for token, n_occurrences in occurrences_map.items() if n_occurrences <= occurrences_map.occurrence_mean)
    return sentence_data[list(set(chain.from_iterable(map(sentence_indices_map.__getitem__, tokens))))]  # type: ignore
