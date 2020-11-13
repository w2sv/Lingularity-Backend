from typing import Optional, List, Set, Iterable
import re

from backend.utils import iterables
from backend.utils.strings import classification, modification, substrings
from backend.utils.strings.utils import _APOSTROPHES, _DASHES


def get_article_stripped_noun(noun_candidate: str) -> Optional[str]:
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


def split_at_uppercase(string: str) -> List[str]:
    return re.findall('[A-Z][a-z]*', string)


def split_multiple(string: str, delimiters: List[str]) -> List[str]:
    """
    >>> split_multiple('wildly,unreasonable:yet,lit!?af', delimiters=list(',:!?'))
    ['wildly', 'unreasonable', 'yet', 'lit', '', 'af'] """

    return modification.replace_multiple(string, delimiters[:-1], delimiters[-1]).split(delimiters[-1])


def substring_occurrence_positions(string: str, substring: str) -> List[int]:
    return [match.start() for match in re.finditer(pattern=substring, string=string)]


def get_meaningful_tokens(text: str, apostrophe_splitting=False) -> List[str]:
    """ Working Principle:
            - strip special characters, unicode remnants
            - break text into distinct tokens
            - remove tokens containing digit(s)

        >>> meaningful_tokens = get_meaningful_tokens("Parce que il n'avait rien à foutre avec ces 3 saloppes qu'il avait rencontrées dans le Bonn17, disait dieu.", apostrophe_splitting=True)
        >>> meaningful_tokens
        ['Parce', 'que', 'il', 'n', 'avait', 'rien', 'à', 'foutre', 'avec', 'ces', 'saloppes', 'qu', 'il', 'avait', 'rencontrées', 'dans', 'le', 'disait', 'dieu'] """

    special_character_stripped = modification.strip_special_characters(text, include_apostrophe=False, include_dash=False)

    split_characters = _DASHES + ' '
    if apostrophe_splitting:
        split_characters += _APOSTROPHES

    tokens = re.split(fr"[{split_characters}]", special_character_stripped)
    return list(filter(lambda token: len(token) and classification.is_digit_free(token), tokens))


def get_unique_meaningful_tokens(text: str, apostrophe_splitting=False) -> Set[str]:
    """
    >>> unique_meaningful_tokens = get_unique_meaningful_tokens("Parce que il n'avait rien à foutre avec ces 3 saloppes qu'il avait rencontrées dans le Bonn17, disait dieu.", apostrophe_splitting=True)
    >>> sorted(unique_meaningful_tokens)
    ['Parce', 'avait', 'avec', 'ces', 'dans', 'dieu', 'disait', 'foutre', 'il', 'le', 'n', 'qu', 'que', 'rencontrées', 'rien', 'saloppes', 'à'] """

    return set(get_meaningful_tokens(text, apostrophe_splitting=apostrophe_splitting))


def common_start(strings: Iterable[str]) -> str:
    """ Returns:
            empty string in case of strings not possessing common start

        >>> common_start(['spaventare', 'spaventoso', 'spazio'])
        'spa'
        >>> common_start(['avventura', 'avventurarsi'])
        'avventura'
        >>> common_start(['nascondersi', 'incolpare'])
        '' """

    buffer = ''
    for strings_i in zip(*strings):
        if len(set(strings_i)) == 1:
            buffer += strings_i[0]
        else:
            break
    return buffer


def longest_continuous_partial_overlap(strings: Iterable[str], min_length=1) -> Optional[str]:
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


def find_quoted_text(text: str) -> List[str]:
    """ Returns:
            text parts located between double(!) quotation marks without marks themselves

    >>> find_quoted_text('He told me to "bugger off" and called me a "filthy skank", whatever that means.')
    ['bugger off', 'filthy skank']
    >>> find_quoted_text("He told me to 'bugger off'")
    [] """

    return re.findall('"(.*?)"', text)


if __name__ == '__main__':
    print(get_meaningful_tokens('Marie hatte d””ie –-asfd überwas zur höhle'))