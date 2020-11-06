import unicodedata
from typing import Iterable

from backend.utils.strings import classification
from backend.utils.strings.utils import _APOSTROPHES


def replace_multiple(text: str, strings: Iterable[str], replacement: str) -> str:
    """
    >>> replace_multiple("That's exactly what i was saying!", strings=["That's", '!'], replacement="Dude")
    'Dude exactly what i was sayingDude' """

    for string in strings:
        text = text.replace(string, replacement)
    return text


def strip_multiple(text: str, strings: Iterable[str]) -> str:
    return replace_multiple(text, strings, replacement='')


def strip_unicode(text: str) -> str:
    return strip_multiple(text, strings=["\u2009", "\u202f", "\xa0", "\xa2", "\u200b", "\xad", "\u200d", "\x08", "\u3000"])


def _to_ascii(string: str) -> str:
    """ Reference: https://stackoverflow.com/questions/517923/what-is-the-best
                   -way-to-remove-accents-normalize-in-a-python-unicode-string

        Returns:
             ascii-transformed string, that is a string whose non-ascii characters have been
             transformed to their respective ascii-equivalent,
             e.g.
                >>> _to_ascii('Odlično')
                'Odlicno'
                >>> _to_ascii('vilkår')
                'vilkar'
                >>> _to_ascii('Söýgi')
                'Soygi'

             whilst such not possessing an equivalent are removed,
                e.g.
                >>> _to_ascii('Hjælp')
                'Hjlp'
                >>> _to_ascii('Dođi')
                'Doi'
                >>> _to_ascii('等等我')
                ''

        Special characters have no impact of the working of this function whatsoever and are returned
            as are """

    return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode()


def strip_accents(string: str) -> str:
    """ Returns:
            original string in case of string not being of latin script,
            otherwise accent stripped string"

        Special characters have no impact of the working of this function whatsoever and are returned
            as are

        >>> strip_accents('perché')
        'perche'
        >>> strip_accents("c'est-à-dire")
        "c'est-a-dire"
        >>> strip_accents('impact')
        'impact'
        >>> strip_accents('走吧')
        '走吧' """

    if classification.is_of_latin_script(string):
        return _to_ascii(string)
    return string


def strip_special_characters(string: str, include_apostrophe=False, include_dash=False) -> str:
    """
    >>> strip_special_characters('''\\wha/Za"„“!#$%&()*+,./:;<=>?@[]^\\_`{|}~»«。¡¿''')
    'whaZa' """

    special_characters = '"„“!#$%&()*+,./:;<=>?@[]^\\_`{|}~»«。¡¿'

    if include_apostrophe:
        special_characters += _APOSTROPHES
    if include_dash:
        special_characters += '-'

    return strip_multiple(string, strings=list(special_characters))


def snake_case_to_title(snake_case_string: str) -> str:
    """
    >>> snake_case_to_title('snake_case_string')
    'Snake Case String' """

    return ' '.join(map(lambda split: split.title(), snake_case_string.split('_')))
