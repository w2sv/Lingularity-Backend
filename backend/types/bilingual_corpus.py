from __future__ import annotations

import collections
from functools import cached_property
from typing import Callable, Counter, Iterable, Iterator

import numpy as np
from textacy.similarity import levenshtein
from tqdm import tqdm
from typing_extensions import TypeAlias

from backend.components.forename_convertor import DEFAULT_FORENAMES
from backend.paths import corpora_path
from backend.utils import iterables
from backend.utils.io import PathLike
from backend.utils.iterables import intersection
from backend.utils.strings.classification import comprises_only_roman_chars, n_non_roman_chars
from backend.utils.strings.extraction import longest_continuous_partial_overlap, meaningful_types, quoted_substrings
from backend.utils.strings.substrings import continuous_substrings
from backend.utils.strings.transformation import special_characters_stripped, strip_multiple


# TODO: move mining related stuff to Miner

SentencePair: TypeAlias = tuple[str, ...]


def percentage_sliced(ndarray: np.ndarray, percentage: float) -> np.ndarray:
    return ndarray[:int(len(ndarray) * percentage)]


class BilingualCorpus(np.ndarray):
    """ np.ndarray[tuple[str, str]] of shape=(N_SENTENCES, 2)

        with:
            BilingualCorpus[:, 0] = REFERENCE LANGUAGE (english if _train_english False, else non-english-language)
            BilingualCorpus[:, 1] = LEARN LANGUAGE (vice-versa) """

    def __new__(cls, language: str, train_english=False) -> BilingualCorpus:
        obj = cls._load(
            corpora_path(language),
            train_english
        )\
            .view(cls)
        obj._train_english = train_english
        return obj

    def __array_finalize__(self, obj, *args, **kwargs):
        if obj is not None:
            self._train_english: bool = getattr(obj, '_train_english', None)  # type: ignore

    @staticmethod
    def _load(path: PathLike, train_english: bool) -> np.ndarray:
        def cleaned_sentence_pairs() -> Iterator[SentencePair]:
            with open(path, 'r', encoding='utf-8') as f:
                for row in f.readlines():
                    newline_char_stripped_row = row[:-1]
                    yield tuple(newline_char_stripped_row.split('\t'))

        ndarray = np.asarray(list(cleaned_sentence_pairs()))

        if train_english:
            ndarray = np.flip(ndarray, axis=1)

        return ndarray

    def strip_bilaterally_present_quotes(self):
        """ Strips double-quotation mark quoted_substring(s) with marks from respective sentence data
            rows if quoted_substring(s) present in both the english and foreign language sentence, possibly
            with special-sign deviation

            i.e. sentence pair:
                'They called me the "King of the Road!"' - Mi hanno chiamato il "King of the Road."'
            would be converted to:
                'They called me the ' - 'Mi hanno chiamato il ' """

        for i_sentence_pair, sentence_pair in enumerate(self):
            _quoted_substrings: Iterator[list[str]] = map(quoted_substrings, sentence_pair)
            _special_characters_stripped: Iterator[Iterator[str]] = ((special_characters_stripped(quote) for quote in quotes) for quotes in _quoted_substrings)
            bilaterally_present_quoted_substrings: set[str] = intersection(map(set, _special_characters_stripped))

            for i_corpus, sentence in enumerate(sentence_pair):
                self[i_sentence_pair, i_corpus] = strip_multiple(
                    sentence,
                    strings=map(
                        lambda quoted_substring: f'"{quoted_substring}"',
                        bilaterally_present_quoted_substrings
                    )
                )

    def dialog_sentences(self) -> Iterator[SentencePair]:
        """ Unused as of now, just-in-case provision """

        is_dialog_sentence = lambda sentence: sentence.count('"') == 4

        for sentence_pair in self:
            if is_dialog_sentence(sentence_pair[0]) and is_dialog_sentence(sentence_pair[1]):
                yield sentence_pair

    class Corpus(np.ndarray):
        """ Abstraction of entirety of sentence data pertaining to one language

            equals: np.ndarray[str] """

        def __new__(cls, data: np.ndarray):
            return data.view(BilingualCorpus.Corpus)

        @cached_property
        def employs_latin_script(self) -> bool:
            N_TOLERATED_NON_ROMAN_CHARS = 2

            return n_non_roman_chars(self.character_set) <= N_TOLERATED_NON_ROMAN_CHARS

        def comprises_tokens(self, query_tokens: list[str], query_portion_percentage=1.0) -> bool:
            """ Args:
                    query_tokens: types which have to be comprised by sentence data in order for method to
                        return True
                    query_portion_percentage: sentence data max length up to which presence of query types will be
                        queried """

            # return False if query types of different script type than sentences
            if self.employs_latin_script != comprises_only_roman_chars(str().join(query_tokens)):
                return False

            query_tokens_set = set(query_tokens)
            for sentence in percentage_sliced(self, percentage=query_portion_percentage):
                meaningful_tokens = meaningful_types(sentence, apostrophe_splitting=False)
                query_tokens_set -= meaningful_tokens
                if not len(query_tokens_set):
                    return True
            return False

        @cached_property
        def character_set(self) -> str:
            """ Returns:
                    comprised characters as sorted string """

            characters = set()

            for sentence in self:
                characters.update(set(sentence))

            return str().join(sorted(characters))

    @cached_property
    def english_corpus(self) -> Corpus:
        return self.Corpus(self[:, int(self._train_english)])

    @cached_property
    def non_english_corpus(self) -> Corpus:
        return self.Corpus(self[:, int(not self._train_english)])

    # -------------------
    # Translation query
    # -------------------
    def query_english_sentence_translation(self, english_sentence: str, query_portion_percentage: float = 1.0) -> str | None:
        """ Args:
                 english_sentence: complete phrase including punctuation whose translation_field ought to be queried
                 query_portion_percentage: percentage of sentence_data file length after exceeding which
                    the query process will be stopped for performance optimization purposes """

        for i, sentence in enumerate(percentage_sliced(self.english_corpus, percentage=query_portion_percentage)):
            if sentence == english_sentence:
                return self.non_english_corpus[i]
        return None

    # -------------------
    # Deduction
    # -------------------

    # -------------------
    # .Proper Nouns
    # -------------------
    def infer_proper_nouns(self) -> set[str]:
        """ Returns:
                set of lowercase proper nouns, deduced by
                    title scripture,
                    length being greater equals 2  (nonexistence of single-character English propernouns),
                    identical bilateral existence in both sentences of one sentence pair,
                    nonexistence of respective lowercase word in both language data columns

            Note:
                strip_bilaterally_present_quotes to be called before invocation in order to eliminate
                uppercase types originating from quotes

            >>> sorted(BilingualCorpus('Croatian').infer_proper_nouns())
             ['android', 'boston', 'braille', 'fi', 'japan', 'john', 'london', 'los', 'louis', 'mama', 'mary', 'new', 'oh', 'sumatra', 'tom', 'tv', 'wi', 'york']

            >>> sorted(BilingualCorpus('Basque').infer_proper_nouns())
            ['alexander', 'bell', 'boston', 'graham', 'mary', 'tokyo', 'tom'] """

        lowercase_english_tokens: set[str] = set()
        lowercase_foreign_language_tokens: set[str] = set()
        uppercase_sentence_pair_tokens_list: list[list[set[str]]] = []

        # accumulate flat language token sets, uppercase sentence pair types
        # list with maintained sentence index dimension
        for sentence_pair in tqdm(self, total=len(self)):
            uppercase_sentence_pair_tokens = []
            for unique_sentence_tokens, lowercase_tokens_cache in zip(
                    list(map(meaningful_types, sentence_pair)),
                    [lowercase_english_tokens, lowercase_foreign_language_tokens]
            ):
                unique_lowercase_tokens = set(filter(lambda token: token.islower(), unique_sentence_tokens))

                lowercase_tokens_cache.update(unique_lowercase_tokens)
                uppercase_sentence_pair_tokens.append(unique_sentence_tokens - unique_lowercase_tokens)

            uppercase_sentence_pair_tokens_list.append(uppercase_sentence_pair_tokens)

        # add candidates to proper nouns which
        #   are at least 2 characters long,
        #   present in both sentences of one sentence pair,
        #   not present in both language lowercase token caches
        proper_nouns: set[str] = set()
        for non_lowercase_sentence_pair_tokens in uppercase_sentence_pair_tokens_list:
            bilaterally_present_tokens = filter(
                lambda token: len(token) > 1,
                iterables.intersection(non_lowercase_sentence_pair_tokens)
            )
            lowered_bilaterally_present_tokens = map(lambda token: token.lower(), bilaterally_present_tokens)
            proper_nouns.update(
                filter(
                    lambda token: token not in lowercase_english_tokens or token not in lowercase_foreign_language_tokens,
                    lowered_bilaterally_present_tokens
                )
            )

        return proper_nouns

    # -------------------
    # .Forename Translations
    # -------------------
    def infer_forename_translations(self) -> list[set[str]]:
        candidates_list: list[set[str]] = []

        for default_forename in DEFAULT_FORENAMES:
            candidates_list.append(self._infer_proper_noun_translation(default_forename))

        for i, candidates in enumerate(candidates_list):
            for candidate in candidates:
                for j, alternating_forename_candidates in enumerate(candidates_list):
                    if i != j:
                        candidates_list[j] = set(
                            filter(
                                lambda alternating_forename_candidate: candidate not in alternating_forename_candidate,
                                alternating_forename_candidates
                            )
                        )

        return candidates_list

    @property
    def _infer_proper_noun_translation(self) -> Callable[[str], set[str]]:
        if self.non_english_corpus.employs_latin_script:
            return self._infer_proper_noun_translations_latin_script_language
        return self._infer_proper_noun_translations_non_latin_script_language

    def _infer_proper_noun_translations_latin_script_language(self, proper_noun: str) -> set[str]:
        MIN_CANDIDATE_PN_LEVENSHTEIN = 0.5
        MAX_FILTERED_CANDIDATE_CONFIRMED_TRANSLATION_LEVENSHTEIN = 0.8

        candidates = set()
        lowercase_words_cache = set()

        for english_sentence, foreign_language_sentence in self:
            if proper_noun in meaningful_types(english_sentence, apostrophe_splitting=True):
                for token in meaningful_types(foreign_language_sentence, apostrophe_splitting=True):
                    if token.istitle() and levenshtein(proper_noun, token) >= MIN_CANDIDATE_PN_LEVENSHTEIN:
                        candidates.add(token)
                    elif token.islower():
                        lowercase_words_cache.add(token)

        filtered_candidates: set[str] = set()
        for candidate in filter(lambda c: c.lower() not in lowercase_words_cache, candidates):
            if all(
                    levenshtein_score <= MAX_FILTERED_CANDIDATE_CONFIRMED_TRANSLATION_LEVENSHTEIN for levenshtein_score
                    in map(lambda filtered_candidate: levenshtein(filtered_candidate, candidate), filtered_candidates)
            ):
                filtered_candidates.add(candidate)

        return filtered_candidates

    def _infer_proper_noun_translations_non_latin_script_language(self, proper_noun: str) -> set[str]:
        CANDIDATE_BAN_INDICATION = -1
        MIN_CANDIDATE_CONFIRMATION_OCCURRENCE = 20
        MAGIC_NUMBER = 3

        translation_candidates: set[str] = set()
        translation_candidate_2_n_occurrences: Counter[str] = collections.Counter()
        translation_comprising_sentence_substrings_cache: list[set[str]] = []
        for english_sentence, foreign_language_sentence in self:
            if proper_noun in meaningful_types(english_sentence, apostrophe_splitting=True):
                foreign_language_sentence = special_characters_stripped(
                    foreign_language_sentence,
                    include_dash=True,
                    include_apostrophe=True
                ).replace(' ', str())

                # skip sentences possessing substring already being present in candidates list
                if len(
                        (intersections := translation_candidates.intersection(
                                continuous_substrings(
                                        foreign_language_sentence,
                                        lengths=set(map(len, translation_candidates))
                                )
                        ))
                ):
                    for _intersection in intersections:
                        translation_candidate_2_n_occurrences[_intersection] += 1

                    if len(intersections) > 1:
                        n_occurrences: list[int] = list(map(translation_candidate_2_n_occurrences.get, intersections))  # type: ignore
                        if any(occurrence >= MIN_CANDIDATE_CONFIRMATION_OCCURRENCE for occurrence in n_occurrences):
                            for n_occurrence, candidate in zip(n_occurrences, intersections):
                                if n_occurrence == MAGIC_NUMBER:
                                    translation_candidates.remove(candidate)
                                    translation_candidate_2_n_occurrences[candidate] = CANDIDATE_BAN_INDICATION

                else:
                    sentence_substrings = set(continuous_substrings(foreign_language_sentence))
                    for i, forename_comprising_sentence_substrings in enumerate(
                            translation_comprising_sentence_substrings_cache
                    ):
                        if len(
                                (substring_intersection := sentence_substrings.intersection(
                                        forename_comprising_sentence_substrings
                                ))
                        ):
                            forename_translation = iterables.longest_value(substring_intersection)
                            if translation_candidate_2_n_occurrences[forename_translation] != CANDIDATE_BAN_INDICATION:
                                translation_candidates.add(forename_translation)
                                translation_candidate_2_n_occurrences[forename_translation] += 1

                                del translation_comprising_sentence_substrings_cache[i]
                                break
                    else:
                        translation_comprising_sentence_substrings_cache.append(sentence_substrings)

        return self._strip_overlaps(translation_candidates)

    @staticmethod
    def _strip_overlaps(translation_candidates: Iterable[str]) -> set[str]:
        if longest_partial_overlap := longest_continuous_partial_overlap(translation_candidates, min_length=2):
            return BilingualCorpus._strip_overlaps(
                list(filter(lambda candidate: longest_partial_overlap not in candidate, translation_candidates)) + [longest_partial_overlap])  # type: ignore
        return set(translation_candidates)