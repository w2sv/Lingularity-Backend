from __future__ import annotations

import random
from typing import Iterable, Iterator, Mapping

from backend.src.components.optional_component import OptionalComponent
from backend.src.metadata import (
    data_beset_countries_language_employed_in,
    get_substitution_forenames_map,
    language_metadata,
    SubstitutionForenamesMap
)
from backend.src.string_resources import string_resources
from backend.src.utils.strings.splitting import split_multiple


DEFAULT_FORENAMES = ('Tom', 'John', 'Mary', 'Alice')  # _DEFAULT_SURNAME = 'Jackson'


class ForenameConvertor(OptionalComponent):
    @staticmethod
    def _available_for(language: str) -> bool:
        if not len(language_metadata[language]['translations']):
            return False
        return bool(data_beset_countries_language_employed_in(language=language))

    def __init__(self, language: str, train_english: bool):
        """ Assumes previous assertion of language convertibility  """

        self._train_english: bool = train_english

        substitution_forenames_map: SubstitutionForenamesMap = get_substitution_forenames_map([language, string_resources['english']][train_english])

        self.demonym: str | None = substitution_forenames_map['demonym']
        self.country: str = substitution_forenames_map['country']
        self._replacement_forenames: list[list[list[str]]] = self._unmap_replacement_forenames(substitution_forenames_map)

        self._default_forename_translations: list[list[str]] = self._unmap_default_forename_translations(language)
        self._uses_latin_script: bool = language_metadata[language]['properties']['usesLatinScript']

    @staticmethod
    def _unmap_replacement_forenames(substitution_forenames_map: SubstitutionForenamesMap) -> list[list[list[str]]]:
        """ Returns:
                3D list with:
                    1st dim: [male_forenames, female_forenames],
                    2nd dim: [latin_spelling, native_spelling],
                    3rd dim: [replacement_forename_1, replacement_forename_2, ..., replacement_forename_n] """

        return [list(gender_dict.values()) for gender_dict in substitution_forenames_map.values() if isinstance(gender_dict, Mapping)]

    @staticmethod
    def _unmap_default_forename_translations(language: str) -> list[list[str]]:
        """ Returns:
                2D list with:
                    1st dim: [Tom, John, Mary, Alice]
                    2nd dim: [translation_1, translation_2, ..., translation_n] """

        return list(map(list, language_metadata[language]['translations']['defaultForenames'].values()))  # type: ignore

    def __call__(self, sentence_pair: list[str]) -> list[str]:

        # invert order of sentence pair in order to line indices up with those of
        # replacement forenames, fallback forename translations in case of English training
        if self._train_english:
            return list(reversed(self._convert_sentence_pair(reversed(sentence_pair))))
        else:
            return self._convert_sentence_pair(sentence_pair)

    def _convert_sentence_pair(self, sentence_pair: Iterable[str]) -> list[str]:
        forename_index_blacklist: list[int | None] = [None, None]  # for prevention of usage of same replacement
        # forename for two different fallback forenames of same gender

        sentence_pair_fragments: list[list[str]] = [sentence.split(' ') for sentence in sentence_pair]

        # iterate over contained forename pairs
        for forename_pair, is_female in self._contained_default_forename_pairs_with_gender(sentence_pair_fragments):
            replacement_forename_index: int | None = None

            # iterate over sentence pair
            for is_foreign_language, fragments in enumerate(sentence_pair_fragments):
                default_forename = forename_pair[is_foreign_language]

                fragment_conversion_mask = self._forename_containment_mask(default_forename, fragments, bool(is_foreign_language))
                replacement_forenames = self._replacement_forenames[is_female][is_foreign_language and not self._uses_latin_script]

                # iterate over sentence tokens
                for fragment_index, (contains_default_forename, fragment) in enumerate(zip(fragment_conversion_mask, fragments)):
                    if contains_default_forename:
                        if replacement_forename_index is None:
                            replacement_forename_index = self._draw_forename_index(len(replacement_forenames), banned_index=forename_index_blacklist[is_female])
                            forename_index_blacklist[is_female] = replacement_forename_index
                        fragments[fragment_index] = fragment.replace(default_forename, replacement_forenames[replacement_forename_index])

                sentence_pair_fragments[is_foreign_language] = fragments

        return [' '.join(sentence_fragments) for sentence_fragments in sentence_pair_fragments]

    @staticmethod
    def _draw_forename_index(n_drawable_forenames: int, banned_index: int | None) -> int:
        drawable_indices = list(range(n_drawable_forenames))
        if banned_index is not None:
            drawable_indices.remove(banned_index)

        return random.choice(drawable_indices)

    def _contained_default_forename_pairs_with_gender(self, sentence_pair_tokens: list[list[str]]) -> Iterator[tuple[tuple[str, str], bool]]:
        """ Returns:
                Iterator of
                    fallback forename pairs contained in sentence pair tokens: Tuple[str, str]
                        first of which is the english forename, second the corresponding foreign language translation_field
                    with corresponding is_female_forename flag: bool

            >>> _sentence_pair_tokens = [['Tom', 'ate', 'Marys', 'tuna.'], ['Tomás', 'mangiava', 'il', 'tonno', 'de', 'Maria.']]
            >>> list(ForenameConvertor('Italian', train_english=False)._contained_default_forename_pairs_with_gender(_sentence_pair_tokens))
            [(('Tom', 'Tomás'), False), (('Mary', 'Maria'), True)]
            """

        for forename_index, (default_forename, forename_translations) in enumerate(zip(DEFAULT_FORENAMES, self._default_forename_translations)):
            if self._forename_comprised_by_tokens(default_forename, sentence_pair_tokens[0], is_foreign_language_sentence=False):
                for forename_translation in forename_translations:
                    if self._forename_comprised_by_tokens(forename_translation, sentence_pair_tokens[1], is_foreign_language_sentence=True):
                        yield (default_forename, forename_translation), forename_index >= 2
                        break

    @classmethod
    def _forename_comprised_by_tokens(
            cls,
            forename: str,
            fragments: list[str],
            is_foreign_language_sentence: bool) -> bool:

        return any(cls._forename_containment_mask(forename, fragments, is_foreign_language_sentence))

    @classmethod
    def _forename_containment_mask(
            cls,
            forename: str,
            tokens: list[str],
            is_foreign_language_sentence: bool) -> Iterator[bool]:

        """ Returns:
                boolean mask of length of tokens whose elements represent whether or not
                the respective tokens contain the passed forename and are hence to be converted

                >>> list(ForenameConvertor._forename_containment_mask('Tom', ["Tom's", "seriously", "messed", "up."], False))
                [True, False, False, False]
                >>> list(ForenameConvertor._forename_containment_mask('Tom', ["Tomorrow", "Mary", "sacrifices", "Toms", "virginity?"], False))
                [False, False, False, True, False]
                """

        for fragment in tokens:
            yield forename in fragment and (is_foreign_language_sentence or cls._contains_english_forename(fragment, forename))

    @staticmethod
    def _contains_english_forename(english_token: str, forename: str) -> bool:
        def is_s_trailed_forename() -> bool:
            return english_token[:-1] == forename and english_token[-1] == 's'

        def is_special_character_delimited_forename() -> bool:
            return split_multiple(english_token, delimiters=list("'?!.,"))[0] == forename

        return is_s_trailed_forename() or is_special_character_delimited_forename()
