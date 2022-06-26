from typing import Iterable
import re
import unicodedata

from backend.utils.strings import classification
from backend.utils.strings._char_sets import APOSTROPHES, DASHES


def replace_multiple(text: str, strings: Iterable[str], replacement: str) -> str:
    """
    >>> replace_multiple("That's exactly what I was saying!", strings=["That's", 'was'], replacement="Dude")
    'Dude exactly what I Dude saying!'
    >>> replace_multiple('snake_case_string', strings=['snake_', '_'], replacement='Pampelmuse')
    'PampelmusecasePampelmusestring' """

    pattern = re.compile('|'.join(map(re.escape, strings)))
    return pattern.sub(replacement, text)


def strip_multiple(string: str, strings: Iterable[str]) -> str:
    return replace_multiple(string, strings, replacement=str())


def unicode_point_stripped(string: str) -> str:
    r"""
    >>> unicode_point_stripped('Odlično')
    'Odlično'
    >>> unicode_point_stripped(r'\u200byup')
    'yup' """

    return UNICODE_POINT_PATTERN.sub(str(), string)


UNICODE_POINT_PATTERN = re.compile(r'\\u[a-z\d]{4}|\\x[a-z\d]{2}')


def asciiized(string: str) -> str:
    """ Reference: https://stackoverflow.com/questions/517923/what-is-the-best
                   -way-to-remove-accents-normalize-in-a-python-unicode-string

        Returns:
             ascii-transformed string, that is a string whose non-ascii characters have been
             transformed to their respective ascii-equivalent,
             e.g.
                >>> asciiized('Odlično')
                'Odlicno'
                >>> asciiized('vilkår')
                'vilkar'
                >>> asciiized('Söýgi')
                'Soygi'

             whilst such not possessing an equivalent are removed,
            e.g.
                >>> asciiized('Hjælp')
                'Hjlp'
                >>> asciiized('Dođi')
                'Doi'
                >>> asciiized('等等我')
                ''

        Special characters have no impact of the working of this function whatsoever and are returned
        as are """

    return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode()


def accent_stripped(string: str) -> str:
    """ Returns:
            original string in case of string not being of latin script,
            otherwise accent stripped string

        Special characters have no impact of the working of this function whatsoever and are returned
            as are

        >>> accent_stripped('perché')
        'perche'
        >>> accent_stripped("c'est-à-dire")
        "c'est-a-dire"
        >>> accent_stripped('impact')
        'impact'
        >>> accent_stripped('走吧')
        '走吧' """

    if classification.comprises_only_roman_chars(string):
        return asciiized(string)
    return string


def special_characters_stripped(string: str, include_apostrophe=False, include_dash=False) -> str:
    """
    >>> special_characters_stripped(r'\\wha/Za"„“”!#$%&()*+,./:;<=>?@[]^\\_`{|}~»«。¡¿')
    'whaZa'
    >>> special_characters_stripped(f'–wha/Za{APOSTROPHES}{DASHES}', include_dash=True, include_apostrophe=True)
    'whaZa' """

    strip_characters = r'"„”“!#$%&()*+,./:;<=>?@[]^\_`{|}~»«。¡¿'

    if include_apostrophe:
        strip_characters += APOSTROPHES
    if include_dash:
        strip_characters += DASHES

    return strip_multiple(string, strings=list(strip_characters))


def snake_case_to_title(snake_case_string: str) -> str:
    """
    >>> snake_case_to_title('snake_case_string')
    'Snake Case String' """

    return ' '.join(map(lambda split: split.title(), snake_case_string.split('_')))
