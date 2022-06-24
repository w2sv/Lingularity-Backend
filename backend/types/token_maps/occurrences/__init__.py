from __future__ import annotations

from collections import Counter, defaultdict
from functools import cached_property
from typing import Iterable

import numpy as np
from tqdm import tqdm

from backend.types.token_maps.custom_mapping import CustomMapping
from backend.types.token_maps.utils import display_creation_kickoff_message


ParaphrasesTokens = list[list[str]]
ParaphrasesTokensList = list[ParaphrasesTokens]

ParaphrasesPOSTagsList = ParaphrasesTokensList


class TokenOccurrencesMap(defaultdict[str, int], CustomMapping):
    """ _Type = DefaultDict[str, int] """

    _INCLUSION_POS_TYPES = {'VERB', 'NOUN', 'ADJ', 'ADV', 'ADP', 'INTJ'}

    def __init__(self, language: str, create=False):
        super().__init__(int, self._data(language, create=create))

    # ----------------
    # Creation
    # ----------------
    def create(self,
               paraphrases_tokens_list: ParaphrasesTokensList,
               paraphrases_pos_tags_list: ParaphrasesPOSTagsList | None):

        if paraphrases_pos_tags_list is not None:
            self._create_with_pos_tags(paraphrases_tokens_list, paraphrases_pos_tags_list)
        else:
            self._create_without_pos_tags(paraphrases_tokens_list)

    @display_creation_kickoff_message('Creating {} without POS tags...')
    def _create_without_pos_tags(self, paraphrases_tokens_list: ParaphrasesTokensList):
        for paraphrases_tokens in tqdm(paraphrases_tokens_list):
            self._insert_paraphrases_tokens(paraphrases_tokens)

    @display_creation_kickoff_message('Creating {} POS tags...')
    def _create_with_pos_tags(self,
                              paraphrases_tokens_list: ParaphrasesTokensList,
                              paraphrases_pos_tags_list: ParaphrasesPOSTagsList):

        for paraphrases_tokens, paraphrases_pos_tags in tqdm(zip(paraphrases_tokens_list, paraphrases_pos_tags_list), total=len(paraphrases_tokens_list)):
            filtered_paraphrases_tokens = ((token for token, pos_tag in zip(paraphrase_tokens, paraphrase_pos_tags) if pos_tag in self._INCLUSION_POS_TYPES) for paraphrase_tokens, paraphrase_pos_tags in zip(paraphrases_tokens, paraphrases_pos_tags))
            self._insert_paraphrases_tokens(paraphrases_tokens=filtered_paraphrases_tokens)

    def _insert_paraphrases_tokens(self, paraphrases_tokens: Iterable[Iterable[str]]):
        for token, occurrences in self._inter_paraphrases_duplicate_stripped_tokens(paraphrases_tokens).items():
            self[token] += occurrences

    @staticmethod
    def _inter_paraphrases_duplicate_stripped_tokens(paraphrases_tokens: Iterable[Iterable[str]]) -> Counter[str]:
        token_counter: Counter[str] = Counter()
        for tokens in paraphrases_tokens:
            token_counter += Counter(tokens) - token_counter
        return token_counter

    # ----------------
    # Creation
    # ----------------
    @cached_property
    def occurrence_mean(self) -> float:
        return np.asarray(list(self.values())).mean()

    @cached_property
    def occurrence_median(self) -> int:
        return int(np.median(list(self.values())))


def create_token_occurrences_map(paraphrases_tokens_list: ParaphrasesTokensList,
                                 paraphrases_pos_tags_list: ParaphrasesPOSTagsList | None) -> TokenOccurrencesMap:

    token_occurrences_map = TokenOccurrencesMap('', create=True)
    token_occurrences_map.create(paraphrases_tokens_list=paraphrases_tokens_list,
                                 paraphrases_pos_tags_list=paraphrases_pos_tags_list)
    return token_occurrences_map
