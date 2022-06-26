import unicodedata

from backend.utils.strings._char_sets import APOSTROPHES
from backend.utils.strings.extraction import split_multiple


def is_digit_free(string: str) -> bool:
    return not any(char.isdigit() for char in string)


def comprises_only_roman_chars(string: str) -> bool:
    """
    >>> comprises_only_roman_chars('ALF, DU KLEINE DRECKFRESSE DU')
    True
    >>> comprises_only_roman_chars("c'est-à-dire")
    True
    >>> comprises_only_roman_chars('Hjælp285;,')
    True
    >>> comprises_only_roman_chars('Ma che cazzo faiº?!')
    True
    >>> comprises_only_roman_chars('等等我')
    False
    >>> comprises_only_roman_chars('HIIIIIER我')
    False
    >>> comprises_only_roman_chars('داوم.')
    False """

    return all(_is_latin(char) for char in filter(lambda char: char.isalpha(), string))


def _is_latin(char: str) -> bool:
    char_name = unicodedata.name(char)
    if not (char_name.startswith('LATIN') or char_name.endswith('ORDINAL INDICATOR')):
        print(char, char_name)
    return char_name.startswith('LATIN') or char_name.endswith('ORDINAL INDICATOR')


def contains_article(noun_candidate: str) -> bool:
    """ Returns:
            True if exactly two distinct types present in noun_candidate if split by whitespace
            as well as apostrophes and the first token, that is the article candidate shorter than
            the second, that is the noun candidate

    >>> contains_article("l'article")
    True
    >>> contains_article("c'est-à-dire")
    False """

    tokens = split_multiple(noun_candidate, delimiters=list(APOSTROPHES) + [' ', '-'])
    return len(tokens) == 2 and len(tokens[0]) < len(tokens[1])
