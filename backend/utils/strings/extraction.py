from __future__ import annotations

import re
from typing import Iterable

from more_itertools import unzip

from backend.utils import iterables
from backend.utils.iterables import unique_contained_value
from backend.utils.strings import substrings
from backend.utils.strings._char_sets import APOSTROPHES, DASHES
from backend.utils.strings.classification import contains_article, is_digit_free
from backend.utils.strings.splitting import split_multiple
from backend.utils.strings.transformation import special_characters_stripped


def article_stripped_noun(noun_candidate: str) -> str | None:
    """ Returns:
            None in case of article identification inability

        >>> article_stripped_noun('il pomeriggio')
        'pomeriggio'
        >>> article_stripped_noun("l'amour")
        'amour'
        >>> article_stripped_noun("amour")

        >>> article_stripped_noun("c'est-à-dire")

        >>> article_stripped_noun('nel guai')
        'guai' """

    if contains_article(noun_candidate):
        return split_multiple(noun_candidate, delimiters=list(APOSTROPHES) + [' '])[1]
    return None


def substring_occurrence_positions(string: str, substring: str) -> list[int]:
    return [match.start() for match in re.finditer(pattern=substring, string=string)]


def meaningful_tokens(text: str, apostrophe_splitting=False) -> list[str]:
    """ - strip special characters & unicode remnants
        - break string into distinct types
        - remove types containing digit(s)

        >>> meaningful_tokens("Parce qu'il n'avait rien à foutre avec ces 3 saloppes, qu'il avait rencontrées dans le Bonn17, disait dieu.", apostrophe_splitting=True)
        ['Parce', 'qu', 'il', 'n', 'avait', 'rien', 'à', 'foutre', 'avec', 'ces', 'saloppes', 'qu', 'il', 'avait',
        'rencontrées', 'dans', 'le', 'disait', 'dieu'] """

    special_character_stripped = special_characters_stripped(text, include_apostrophe=False, include_dash=False)

    split_characters = DASHES + ' '
    if apostrophe_splitting:
        split_characters += APOSTROPHES

    tokens = re.split(f"[{split_characters}]", special_character_stripped)
    return list(filter(lambda token: len(token) and is_digit_free(token), tokens))


def meaningful_types(text: str, apostrophe_splitting=False) -> set[str]:
    """
    >>> sorted(meaningful_types("Parce que il n'avait rien à foutre avec ces 3 saloppes qu'il avait rencontrées dans le Bonn17, disait dieu.", apostrophe_splitting=True))
    ['Parce', 'avait', 'avec', 'ces', 'dans', 'dieu', 'disait', 'foutre', 'il', 'le', 'n', 'qu', 'que', 'rencontrées', 'rien', 'saloppes', 'à'] """

    return set(meaningful_tokens(text, apostrophe_splitting=apostrophe_splitting))


def longest_common_prefix(strings: Iterable[str]) -> str:
    """ Returns:
            empty string in case of strings not possessing common start

        >>> longest_common_prefix(['spaventare', 'spaventoso', 'spazio'])
        'spa'
        >>> longest_common_prefix(['avventura', 'avventurarsi'])
        'avventura'
        >>> longest_common_prefix(['nascondersi', 'incolpare'])
        '' """

    common_prefix = ''
    for strings_i in unzip(strings):
        if (unique_value := unique_contained_value(strings_i)) is not None:
            common_prefix += unique_value
        else:
            break
    return common_prefix


def longest_continuous_partial_overlap(strings: Iterable[str], min_length=1) -> str | None:
    """ Returns:
            longest retrievable substring of length >= min_length present in at least
            two strings at any position respectively, None if no such substring being
            present

    >>> longest_continuous_partial_overlap(['メアリーが', 'トムは', 'トムはメアリーを', 'メアリー', 'トムはマリ', 'いた', 'メアリーは'])
    'メアリー'
    >>> longest_continuous_partial_overlap(['amatur', 'masochist', 'erlaucht', 'manko'])
    'ma'
    >>> longest_continuous_partial_overlap(['mast', 'merk', 'wucht'], min_length=2)

    """

    buffer = ''
    substrings_list = list(map(lambda string: set(substrings.start_including_substrings(string)), strings))
    for i, _substrings in enumerate(substrings_list):
        for comparison in substrings_list[i + 1:]:
            buffer = iterables.longest_value([buffer, iterables.longest_value(_substrings & comparison | {''})])
    return [None, buffer][len(buffer) > min_length]


def quoted_substrings(string: str) -> list[str]:
    """ Returns:
            string parts located between double(!) quotation marks without marks themselves

    >>> quoted_substrings('He told me to "bugger off" and called me a "filthy skank", whatever that means.')
    ['bugger off', 'filthy skank']
    >>> quoted_substrings("He told me to 'bugger off'")
    [] """

    return re.findall('"(.*?)"', string)
