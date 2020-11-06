from backend.utils.strings import modification, extraction
from backend.utils.strings.utils import _APOSTROPHES


def is_digit_free(string: str) -> bool:
    return not any(char.isdigit() for char in string)


def is_of_latin_script(string: str, remove_non_alphabetic_characters=True) -> bool:
    """ Args:
            string: regarding which to be determined whether of latin script
            remove_non_alphabetic_characters: triggers removal of special characters as well as white-spaces
                if set to True, solely for prevention of redundant stripping if already having taken place, since
                REMOVAL INTEGRAL FOR PROPER FUNCTION WORKING

        Returns:
            True if at least 80% of alphabetic characters amongst string pertaining to latin script,
            False otherwise """

    MIN_LATIN_CHARACTER_PERCENTAGE = 80

    if remove_non_alphabetic_characters:
        string = modification.strip_special_characters(string, include_apostrophe=True, include_dash=True).replace(' ', '')

    return len(modification._to_ascii(string)) / len(string) > (MIN_LATIN_CHARACTER_PERCENTAGE / 100)


def contains_article(noun_candidate: str) -> bool:
    """ Returns:
            True if exactly two distinct tokens present in noun_candidate if split by whitespace
            as well as apostrophes and the first token, that is the article candidate shorter than
            the second, that is the noun candidate

    >>> contains_article("l'article")
    True
    >>> contains_article("c'est-à-dire")
    False """

    return len((tokens := extraction.split_multiple(noun_candidate, delimiters=list(_APOSTROPHES) + [' ', '-']))) == 2 and len(
        tokens[0]) < len(tokens[1])


def contains_unicode(text: str) -> bool:
    TOLERATED_FOLLOWUP_CHARS = ['t', 'n']

    for i, char in enumerate((text_repr := repr(text))):
        if '\\' in char and text_repr[i+1] not in TOLERATED_FOLLOWUP_CHARS:
            return True
    return False
