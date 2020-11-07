""" google libraries demanding language arguments to be passed in corresponding language,
    as well as in the bulk of cases 2-letter comprising abbreviation,
        e.g. Spanish -> es
             German -> de
             French -> fr """

from typing import Optional, Dict, List
from abc import ABC


class GoogleOp(ABC):
    __slots__ = '_LANGUAGE_2_IDENTIFIER'

    _LANGUAGE_2_IDENTIFIER: Dict[str, str]  # uppercase language to lowercase identifier,
    # e.g. {'Afrikaans': 'af', 'Albanian': 'sq', ...}

    def available_for(self, language: str) -> bool:
        return self._get_identifier(language) is not None

    def _get_identifier(self, query_language: str) -> Optional[str]:
        """ Args:
                query_language: written out titular language in English,
                    e.g. 'Spanish'

            Returns:
                the first matching google language identifier """

        print('Calculating')

        # return identifier if query_language is amongst language identifiers as is
        if identifier := self._LANGUAGE_2_IDENTIFIER.get(query_language):
            return identifier

        # frisk LANGUAGE_2_IDENTIFIER for identifier
        for _language, identifier in self._LANGUAGE_2_IDENTIFIER.items():
            if query_language in _language:
                return identifier

        return None

    def get_variety_choices(self, query_language: str) -> Optional[List[str]]:
        """ Returns:
                List of available language variations in case of availability of more than 1,
                otherwise None, e.g.

                TextToSpeech.get_variety_choices('french')
                    ['French (Canada)', 'French (France)']  """

        dialect_choices = list(filter(lambda language: query_language != language and query_language in language, self._LANGUAGE_2_IDENTIFIER.keys()))
        return [None, dialect_choices][len(dialect_choices) > 1]
