from __future__ import annotations

import re
from typing import Iterable

from backend.utils import iterables
from backend.utils.strings import classification, modification, substrings
from backend.utils.strings._utils import _APOSTROPHES, _DASHES


def get_article_stripped_noun(noun_candidate: str) -> str | None:
    """ Returns:
            None in case of article identification inability

        >>> get_article_stripped_noun('il pomeriggio')
        'pomeriggio'
        >>> get_article_stripped_noun("l'amour")
        'amour'
        >>> get_article_stripped_noun("amour")

        >>> get_article_stripped_noun("c'est-à-dire")

        >>> get_article_stripped_noun('nel guai')
        'guai' """

    if classification.contains_article(noun_candidate):
        return split_multiple(noun_candidate, delimiters=list(_APOSTROPHES) + [' '])[1]
    return None


def split_at_uppercase(string: str) -> list[str]:
    return re.findall('[A-Z][a-z]*', string)


def split_multiple(string: str, delimiters: list[str]) -> list[str]:
    """
    >>> split_multiple('wildly,unreasonable:yet,lit!?af', delimiters=list(',:!?'))
    ['wildly', 'unreasonable', 'yet', 'lit', '', 'af'] """

    return modification.replace_multiple(string, delimiters[:-1], delimiters[-1]).split(delimiters[-1])


def substring_occurrence_positions(string: str, substring: str) -> list[int]:
    return [match.start() for match in re.finditer(pattern=substring, string=string)]


def meaningful_tokens(text: str, apostrophe_splitting=False) -> list[str]:
    """ - strip special characters & unicode remnants
        - break text into distinct types
        - remove types containing digit(s)

        >>> meaningful_tokens("Parce qu'il n'avait rien à foutre avec ces 3 saloppes, qu'il avait rencontrées dans le Bonn17, disait dieu.", apostrophe_splitting=True)
        ['Parce', 'qu', 'il', 'n', 'avait', 'rien', 'à', 'foutre', 'avec', 'ces', 'saloppes', 'qu', 'il', 'avait',
        'rencontrées', 'dans', 'le', 'disait', 'dieu'] """

    special_character_stripped = modification.strip_special_characters(text, include_apostrophe=False, include_dash=False)

    split_characters = _DASHES + ' '
    if apostrophe_splitting:
        split_characters += _APOSTROPHES

    tokens = re.split(fr"[{split_characters}]", special_character_stripped)
    return list(filter(lambda token: len(token) and classification.is_digit_free(token), tokens))


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

    buffer = ''
    for strings_i in zip(*strings):
        if len(set(strings_i)) == 1:
            buffer += strings_i[0]
        else:
            break
    return buffer


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


def find_quoted_text(text: str) -> list[str]:
    """ Returns:
            text parts located between double(!) quotation marks without marks themselves

    >>> find_quoted_text('He told me to "bugger off" and called me a "filthy skank", whatever that means.')
    ['bugger off', 'filthy skank']
    >>> find_quoted_text("He told me to 'bugger off'")
    [] """

    return re.findall('"(.*?)"', text)
