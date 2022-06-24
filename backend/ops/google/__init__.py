""" google libraries demanding language arguments to be passed in corresponding language,
    as well as in the bulk of cases 2-letter comprising abbreviation,
        e.g. Spanish -> es
             German -> de
             French -> fr """
from __future__ import annotations

from abc import ABC, abstractmethod


class GoogleOperationClient(ABC):
    # uppercase language to lowercase identifier,
    # e.g. {'Afrikaans': 'af', 'Albanian': 'sq', ...}
    _LANGUAGE_2_IETF_TAG: dict[str, str]

    @classmethod
    def available_for(cls, language: str) -> bool:
        return cls._get_identifier(language) is not None

    @classmethod
    def _get_identifier(cls, language: str) -> str | None:
        """ Args:
                language: written out titular language in English,
                    e.g. 'Spanish'

            Returns:
                the first matching google language identifier """

        # return identifier if query_language is amongst language identifiers as is
        if identifier := cls._LANGUAGE_2_IETF_TAG.get(language):
            return identifier

        # frisk _LANGUAGE_2_IDENTIFIER for identifier
        for _language, identifier in cls._LANGUAGE_2_IETF_TAG.items():
            if language in _language:
                return identifier

        return None

    def __init__(self, language: str):
        self.language = language
        self._language_identifier: str = self._get_identifier(language)  # type: ignore
        self.language_variety_choices: list[str] = self._get_variety_choices()

    @abstractmethod
    def _get_variety_choices(self) -> list[str]:
        """  """

    def _deduced_variety_choices(self) -> list[str]:
        """ Returns:
                List of available language variations in case of availability of more than 1,
                otherwise None, e.g.

                TTS._get_variety_choices('french')
                    ['French (Canada)', 'French (France)']

            TODO: reintegrate for chinese regarding tts """

        return list(
            filter(
                lambda language: self.language != language and self.language in language,
                self._LANGUAGE_2_IETF_TAG.keys()
            )
        )