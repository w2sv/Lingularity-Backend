from collections import defaultdict
from typing import Iterator

from backend.src.types.bilingual_corpus import BilingualCorpus
from backend.src.types.token_maps import get_token_maps, Token2ComprisingSentenceIndices, TokenOccurrencesMap
from backend.src.utils import iterables


def filter_sentence_data(sentence_data: BilingualCorpus, language: str) -> BilingualCorpus:
    sentence_indices_map, occurrences_map = get_token_maps(language)

    sentence_indices_with_comprising_occurrences = _sentence_indices_with_comprising_tokens(sentence_indices_map, occurrences_map)
    sentence_indices = (sentence_index for sentence_index, comprising_occurrences in sentence_indices_with_comprising_occurrences if all((occurrence >= occurrences_map.occurrence_mean for occurrence in comprising_occurrences)))
    return sentence_data[list(sentence_indices)]  # type: ignore


def _sentence_indices_with_comprising_tokens(sentence_indices_map: Token2ComprisingSentenceIndices,
                                             occurrences_map: TokenOccurrencesMap) -> Iterator[tuple[int, Iterator[int]]]:

    sentence_index_2_comprising_tokens: dict[int, set[str]] = defaultdict(set)
    for token, sentence_indices in sentence_indices_map.items():
        for sentence_index in sentence_indices:
            sentence_index_2_comprising_tokens[sentence_index].add(token)

    return ((sentence_index, iterables.none_stripped(map(occurrences_map.get, comprising_tokens))) for sentence_index, comprising_tokens in sentence_index_2_comprising_tokens.items())  # type: ignore
