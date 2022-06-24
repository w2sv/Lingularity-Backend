from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from itertools import repeat

from backend.types.token_maps.custom_mapping import CustomMapping
from backend.types.token_maps.utils import display_creation_kickoff_message
from backend.utils import iterables, strings


SentenceIndex2UniqueTokens = dict[int, set[str]]


class SegmentSentenceIndicesMap(defaultdict[str, list[int]], CustomMapping, ABC):
    """ Interface for map classes comprising an association of
          unique, LOWERCASE and RELEVANT tokens (unnormalized/normalized): str
                to the
          sentence indices corresponding to the bilateral sentence data in
          which they occur, in either_or an inflected form (NormalizedTokenMaps)
          or as they are(TokenSentenceIndicesMap): List[int] """

    def __init__(self, language: str, create: bool):
        super().__init__(list, self._data(language, create=create))

    @display_creation_kickoff_message('Creating {}...')
    def create(self, sentence_index_2_unique_tokens: SentenceIndex2UniqueTokens):
        for sentence_index, tokens in sentence_index_2_unique_tokens.items():
            for token in tokens:
                self[token].append(sentence_index)

    def tokenize_with_pos_tags(self, sentence: str) -> list[tuple[str, str]]:
        # TODO: Implement in spacy devoid fashion

        return list(zip(self.tokenize(sentence), repeat('')))

    @abstractmethod
    def tokenize(self, sentence: str) -> list[str]:
        pass

    # ------------------
    # Sentence Index Query
    # ------------------
    @abstractmethod
    def query_sentence_indices(self, vocable_entry: str) -> list[int] | None:
        """ Queries indices of sentences in which the relevant tokens of the passed vocable_entry occur

            Args:
                vocable_entry: raw vocable entry of the same language as the tokens present in map """
        pass

    def _find_best_fit_sentence_indices(self, relevance_sorted_tokens: list[str]) -> list[int] | None:
        """ Working Principle:
                - query sentence indices corresponding to distinct tokens present in relevance_sorted_tokens
                    -> return None if no sentence indices found at all
                - consecutively pop sentence indices element from sentence indices list, starting with the
                    ones corresponding to tokens of lower relevance, and return the intersection between
                    the remaining sentence indices elements if existent
                - return sentence indices of most relevant vocable if the only one remaining """

        relevance_sorted_sentence_indices: list[list[int]] = iterables.none_stripped((self.get(token) for token in relevance_sorted_tokens))  # type: ignore

        if not len(relevance_sorted_sentence_indices):
            return None

        relevance_sorted_unique_sentence_indices: list[set[int]] = list(map(set, relevance_sorted_sentence_indices))  # type: ignore
        while len(relevance_sorted_unique_sentence_indices) > 1:
            if len((remaining_sentence_indices_list_intersection := iterables.intersection(relevance_sorted_unique_sentence_indices))):
                return list(remaining_sentence_indices_list_intersection)
            relevance_sorted_unique_sentence_indices.pop()

        return list(relevance_sorted_unique_sentence_indices[0])

    @staticmethod
    def _get_length_sorted_meaningful_tokens(vocable_entry: str) -> list[str]:
        if (article_stripped_noun := strings.get_article_stripped_noun(vocable_entry)) is not None:
            return [article_stripped_noun]
        return sorted(strings.get_meaningful_tokens(vocable_entry, apostrophe_splitting=True), key=lambda token: len(token))
