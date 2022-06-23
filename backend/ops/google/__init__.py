""" google libraries demanding language arguments to be passed in corresponding language,
    as well as in the bulk of cases 2-letter comprising abbreviation,
        e.g. Spanish -> es
             German -> de
             French -> fr """
import abc
from abc import ABC
from typing import Dict, List, Optional


class GoogleOperation(ABC):
    def __init__(self, language_2_ietf_tag: Dict[str, str]):
        self.language_2_ietf_tag = language_2_ietf_tag  # uppercase language to lowercase identifier,
                                                        # e.g. {'Afrikaans': 'af', 'Albanian': 'sq', ...}

    def available_for(self, language: str) -> bool:
        return self._get_identifier(language) is not None

    def _get_identifier(self, query_language: str) -> Optional[str]:
        """ Args:
                query_language: written out titular language in English,
                    e.g. 'Spanish'

            Returns:
                the first matching google language identifier """

        # return identifier if query_language is amongst language identifiers as is
        if identifier := self.language_2_ietf_tag.get(query_language):
            return identifier

        # frisk _LANGUAGE_2_IDENTIFIER for identifier
        for _language, identifier in self.language_2_ietf_tag.items():
            if query_language in _language:
                return identifier

        return None

    @abc.abstractmethod
    def get_variety_choices(self, query_language: str) -> Optional[List[str]]:
        """  """

    def _deduced_variety_choices(self, query_language: str) -> Optional[List[str]]:
        """ Returns:
                List of available language variations in case of availability of more than 1,
                otherwise None, e.g.

                TTSClient.get_variety_choices('french')
                    ['French (Canada)', 'French (France)']  """

        return list(
            filter(
                lambda language: query_language != language and query_language in language,
                self.language_2_ietf_tag.keys()
            )
        ) or None