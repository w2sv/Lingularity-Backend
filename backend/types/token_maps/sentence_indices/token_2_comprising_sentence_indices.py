from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import repeat

from backend.types.token_maps.custom_mapping import TokenMap
from backend.types.token_maps.utils import display_creation_kickoff_message
from backend.utils import iterables
from backend.utils.strings import get_article_stripped_noun, meaningful_types


SentenceIndex2UniqueTokens = dict[int, set[str]]


class Token2ComprisingSentenceIndices(TokenMap[list[int]], ABC):
    """ TokenMap base class, comprising an association of
          unique, LOWERCASE and RELEVANT types (unnormalized/normalized): str
                to the
          sentence indices corresponding to the bilateral sentence data in
          which they occur, in either an inflected form (NormalizedTokenMaps)
          or as they are(Token2SentenceIndicesMap): List[int] """

    @staticmethod
    def _factory():
        return list

    @staticmethod
    @abstractmethod
    def is_available_for(language: str) -> bool:
        """ Args:
                language: titled language """

    @display_creation_kickoff_message('Creating {}...')
    def create(self, sentence_index_2_unique_tokens: SentenceIndex2UniqueTokens):
        for sentence_index, tokens in sentence_index_2_unique_tokens.items():
            for token in tokens:
                self[token].append(sentence_index)

    def best_possibly_normalized_types_with_pos(self, sentence: str) -> set[tuple[str, str]]:
        # TODO: Implement in spacy devoid fashion

        return set(zip(self.best_possibly_normalized_meaningful_types(sentence), repeat('')))

    @abstractmethod
    def best_possibly_normalized_meaningful_types(self, sentence: str) -> set[str]:
        """  """

    # ------------------
    # Sentence Index Query
    # ------------------
    @abstractmethod
    def comprising_sentence_indices(self, vocable: str) -> list[int] | None:
        """ Queries indices of sentences in which the relevant types of the passed vocable_entry occur

            Args:
                vocable: raw, unprocessed vocable of the same language as the types present in map;
                         may comprise singular word / word group | digits / special characters... """

    def _find_best_fit_sentence_indices(self, relevance_sorted_types: list[str]) -> list[int] | None:
        """ Working Principle:
                - query sentence indices corresponding to distinct types present in relevance_sorted_types
                    -> return None if no sentence indices found at all
                - consecutively pop sentence indices element from sentence indices list, starting with the
                    ones corresponding to types of lower relevance, and return the intersection between
                    the remaining sentence indices elements if existent
                - return sentence indices of most relevant vocable if the only one remaining """

        relevance_sorted_sentence_indices: list[list[int]] = iterables.none_stripped((self.get(token) for token in relevance_sorted_types))  # type: ignore

        if not len(relevance_sorted_sentence_indices):
            return None

        relevance_sorted_unique_sentence_indices: list[set[int]] = list(map(set, relevance_sorted_sentence_indices))  # type: ignore
        while len(relevance_sorted_unique_sentence_indices) > 1:
            if len((remaining_sentence_indices_list_intersection := iterables.intersection(relevance_sorted_unique_sentence_indices))):
                return list(remaining_sentence_indices_list_intersection)
            relevance_sorted_unique_sentence_indices.pop()

        return list(relevance_sorted_unique_sentence_indices[0])

    @staticmethod
    def _length_sorted_meaningful_types(vocable_entry: str) -> list[str]:
        if (article_stripped_noun := get_article_stripped_noun(vocable_entry)) is not None:
            return [article_stripped_noun]
        return sorted(
            meaningful_types(
                vocable_entry,
                apostrophe_splitting=True
            ),
            key=len
        )
