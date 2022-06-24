from __future__ import annotations

import collections
from functools import cached_property
from typing import Callable, Counter, Iterable, Iterator

from more_itertools import unzip
import numpy as np
from textacy.similarity import levenshtein
from tqdm import tqdm
from typing_extensions import TypeAlias

from backend.components.forename_convertor import DEFAULT_FORENAMES
from backend.paths import corpus_path
from backend.utils import iterables
from backend.utils.io import PathLike
from backend.utils.strings import (
    continuous_substrings,
    find_quoted_text,
    get_unique_meaningful_tokens,
    is_of_latin_script,
    longest_continuous_partial_overlap
)
from backend.utils.strings.modification import strip_multiple, strip_special_characters, strip_unicode


# TODO: move mining related stuff to Miner

SentencePair: TypeAlias = tuple[str, str]

class Corpus(np.ndarray):
    """ Abstraction of sentence pair data

        equals np.ndarray[List[List[str]], i.e. ndim == 2,
        with, in case of _train_english being False:
            Corpus[:, 0] = english sentences,
            Corpus[:, 1] = translations
        otherwise vice-versa """

    _train_english: bool = False

    def __new__(cls, language: str, train_english=False):
        """ Downloads sentence data if necessary """

        cls._train_english = train_english

        return cls._load(corpus_path(language), train_english).view(Corpus)

    @staticmethod
    def _load(_sentence_data_path: PathLike, train_english: bool) -> np.ndarray:
        processed_sentence_data = []

        with open(_sentence_data_path, 'r', encoding='utf-8', errors='strict') as sentence_data_file:
            for sentence_pair_line in sentence_data_file.readlines():
                sentence_pair = strip_unicode(sentence_pair_line[:-1]).split('\t')

                if train_english:
                    sentence_pair = list(reversed(sentence_pair))

                processed_sentence_data.append(sentence_pair)

        return np.asarray(processed_sentence_data)

    def strip_bilaterally_present_quotes(self):
        """ Strips double-quotation mark quote(s) with marks from respective sentence data
            rows if quote(s) present in both the english and foreign language sentence, possibly
            with special-sign deviation

            i.e. sentence pair:
                'They called me the "King of the Road!"' - Mi hanno chiamato il "King of the Road."'
            would be converted to:
                'They called me the ' - 'Mi hanno chiamato il ' """

        for i, sentence_pair in enumerate(self):
            sentence_pair_quotes = map(find_quoted_text, sentence_pair)
            bilaterally_present_quote_pairs = filter(lambda quote_pair: iterables.contains_unique_value(map(lambda quote: strip_special_characters(quote), quote_pair)), zip(*sentence_pair_quotes))

            for j, (sentence, comprising_quotes) in enumerate(zip(sentence_pair, unzip(bilaterally_present_quote_pairs))):
                self[i, j] = strip_multiple(sentence, strings=map(lambda quote: '"' + quote + '"', comprising_quotes))

    # -------------------
    # Columns
    # -------------------
    class Column(np.ndarray):
        """ Abstraction of entirety of sentence data pertaining to one language

            equals: np.ndarray[str] """

        def __new__(cls, sentence_data_column: np.ndarray):
            return sentence_data_column.view(Corpus.Column)

        @cached_property
        def uses_latin_script(self) -> bool:
            return is_of_latin_script(self[-1], remove_non_alphabetic_characters=True)

        def comprises_tokens(self, query_tokens: list[str], query_length_percentage=1.0) -> bool:
            """ Args:
                    query_tokens: tokens which have to be comprised by sentence data in order for method to
                        return True
                    query_length_percentage: sentence data max length up to which presence of query tokens will be
                        queried """

            # return False if query tokens of different script type than sentences
            if self.uses_latin_script != is_of_latin_script(''.join(query_tokens), remove_non_alphabetic_characters=False):
                return False

            query_tokens_set = set(query_tokens)
            for sentence in self[:int(len(self) * query_length_percentage)]:
                meaningful_tokens = get_unique_meaningful_tokens(sentence, apostrophe_splitting=False)
                query_tokens_set -= meaningful_tokens
                if not len(query_tokens_set):
                    return True
            return False

        @property
        def comprising_characters(self) -> set[str]:
            characters = set()

            for sentence in self:
                characters.update(set(list(sentence)))

            return characters

    @cached_property
    def english_sentences(self) -> Column:
        return self.Column(self[:, 0 + int(self._train_english)])

    @cached_property
    def foreign_language_sentences(self) -> Column:
        return self.Column(self[:, 1 - int(self._train_english)])

    # -------------------
    # Translation query
    # -------------------
    def query_translation(self, english_sentence: str, file_max_length_percentage: float = 1.0) -> str | None:
        """ Args:
                 english_sentence: complete phrase including punctuation whose translation_field ought to be queried
                 file_max_length_percentage: percentage of sentence_data file length after exceeding which
                    the query process will be stopped for performance optimization purposes """

        for content, i in ((sentence_pair[0], i) for i, sentence_pair in
                           enumerate(self[:int(len(self) * file_max_length_percentage)])):
            if content == english_sentence:
                return self[i, 1]
        return None

    # -------------------
    # Deduction
    # -------------------

    # -------------------
    # .Proper Nouns
    # -------------------
    def deduce_proper_nouns(self) -> set[str]:
        """ Returns:
                set of lowercase proper nouns, deduced by
                    title scripture,
                    length being greater equals 2  (nonexistence of single-character English propernouns),
                    identical bilateral existence in both sentences of one sentence pair,
                    nonexistence of respective lowercase word in both language data columns

            Note:
                strip_bilaterally_present_quotes to be called before invocation in order to eliminate
                uppercase tokens originating from quotes

            >>> sorted(Corpus('Croatian').deduce_proper_nouns())
             ['android', 'boston', 'braille', 'fi', 'japan', 'john', 'london', 'los', 'louis', 'mama', 'mary', 'new', 'oh', 'sumatra', 'tom', 'tv', 'wi', 'york']

            >>> sorted(Corpus('Basque').deduce_proper_nouns())
            ['alexander', 'bell', 'boston', 'graham', 'mary', 'tokyo', 'tom'] """

        lowercase_english_tokens: set[str] = set()
        lowercase_foreign_language_tokens: set[str] = set()
        uppercase_sentence_pair_tokens_list: list[list[set[str]]] = []

        # accumulate flat language token sets, uppercase sentence pair tokens
        # list with maintained sentence index dimension
        for sentence_pair in tqdm(self._zipped_sentence_iterator, total=len(self)):
            uppercase_sentence_pair_tokens = []
            for unique_sentence_tokens, lowercase_tokens_cache in zip(list(map(get_unique_meaningful_tokens, sentence_pair)), [lowercase_english_tokens, lowercase_foreign_language_tokens]):
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
            bilaterally_present_tokens = filter(lambda token: len(token) > 1, iterables.intersection(non_lowercase_sentence_pair_tokens))
            lowered_bilaterally_present_tokens = map(lambda token: token.lower(), bilaterally_present_tokens)
            proper_nouns.update(filter(lambda token: token not in lowercase_english_tokens or token not in lowercase_foreign_language_tokens, lowered_bilaterally_present_tokens))

        return proper_nouns

    # -------------------
    # .Forename Translations
    # -------------------
    def deduce_forename_translations(self) -> list[set[str]]:
        candidates_list: list[set[str]] = []

        for default_forename in DEFAULT_FORENAMES:
            candidates_list.append(self._deduce_proper_noun_translation(default_forename))

        for i, candidates in enumerate(candidates_list):
            for candidate in candidates:
                for j, alternating_forename_candidates in enumerate(candidates_list):
                    if i != j:
                        candidates_list[j] = set(filter(lambda alternating_forename_candidate: candidate not in alternating_forename_candidate, alternating_forename_candidates))

        return candidates_list

    @property
    def _deduce_proper_noun_translation(self) -> Callable[[str], set[str]]:
        if self.foreign_language_sentences.uses_latin_script:
            return self._deduce_proper_noun_translations_latin_script_language
        return self._deduce_proper_noun_translations_non_latin_script_language

    def _deduce_proper_noun_translations_latin_script_language(self, proper_noun: str) -> set[str]:
        MIN_CANDIDATE_PN_LEVENSHTEIN = 0.5
        MAX_FILTERED_CANDIDATE_CONFIRMED_TRANSLATION_LEVENSHTEIN = 0.8

        candidates = set()
        lowercase_words_cache = set()

        for english_sentence, foreign_language_sentence in self._zipped_sentence_iterator:
            if proper_noun in get_unique_meaningful_tokens(english_sentence, apostrophe_splitting=True):
                for token in get_unique_meaningful_tokens(foreign_language_sentence, apostrophe_splitting=True):
                    if token.istitle() and levenshtein(proper_noun, token) >= MIN_CANDIDATE_PN_LEVENSHTEIN:
                        candidates.add(token)
                    elif token.islower():
                        lowercase_words_cache.add(token)

        filtered_candidates: set[str] = set()
        for candidate in filter(lambda c: c.lower() not in lowercase_words_cache, candidates):
            if all(levenshtein_score <= MAX_FILTERED_CANDIDATE_CONFIRMED_TRANSLATION_LEVENSHTEIN for levenshtein_score in map(lambda filtered_candidate: levenshtein(filtered_candidate, candidate), filtered_candidates)):
                filtered_candidates.add(candidate)

        return filtered_candidates

    def _deduce_proper_noun_translations_non_latin_script_language(self, proper_noun: str) -> set[str]:
        CANDIDATE_BAN_INDICATION = -1
        MIN_CANDIDATE_CONFIRMATION_OCCURRENCE = 20
        MAGIC_NUMBER = 3

        translation_candidates: set[str] = set()
        translation_candidate_2_n_occurrences: Counter[str] = collections.Counter()
        translation_comprising_sentence_substrings_cache: list[set[str]] = []
        for english_sentence, foreign_language_sentence in self._zipped_sentence_iterator:
            if proper_noun in get_unique_meaningful_tokens(english_sentence, apostrophe_splitting=True):
                foreign_language_sentence = strip_special_characters(foreign_language_sentence, include_dash=True, include_apostrophe=True).replace(' ', '')

                # skip sentences possessing substring already being present in candidates list
                if len((intersections := translation_candidates.intersection(continuous_substrings(foreign_language_sentence, lengths=set(map(len, translation_candidates)))))):
                    for intersection in intersections:
                        translation_candidate_2_n_occurrences[intersection] += 1

                    if len(intersections) > 1:
                        n_occurrences: List[int] = list(map(translation_candidate_2_n_occurrences.get, intersections))  # type: ignore
                        if any(occurrence >= MIN_CANDIDATE_CONFIRMATION_OCCURRENCE for occurrence in n_occurrences):
                            for n_occurrence, candidate in zip(n_occurrences, intersections):
                                if n_occurrence == MAGIC_NUMBER:
                                    translation_candidates.remove(candidate)
                                    translation_candidate_2_n_occurrences[candidate] = CANDIDATE_BAN_INDICATION

                else:
                    sentence_substrings = set(continuous_substrings(foreign_language_sentence))
                    for i, forename_comprising_sentence_substrings in enumerate(translation_comprising_sentence_substrings_cache):
                        if len((substring_intersection := sentence_substrings.intersection(forename_comprising_sentence_substrings))):
                            forename_translation = iterables.longest_value(substring_intersection)
                            if translation_candidate_2_n_occurrences[forename_translation] != CANDIDATE_BAN_INDICATION:
                                translation_candidates.add(forename_translation)
                                translation_candidate_2_n_occurrences[forename_translation] += 1

                                del translation_comprising_sentence_substrings_cache[i]
                                break
                    else:
                        translation_comprising_sentence_substrings_cache.append(sentence_substrings)

        return self._strip_overlaps(translation_candidates)

    @property
    def _zipped_sentence_iterator(self) -> Iterator[tuple[str, str]]:
        return zip(self.english_sentences, self.foreign_language_sentences)

    @staticmethod
    def _strip_overlaps(translation_candidates: Iterable[str]) -> set[str]:
        if longest_partial_overlap := longest_continuous_partial_overlap(translation_candidates, min_length=2):
            return Corpus._strip_overlaps(list(filter(lambda candidate: longest_partial_overlap not in candidate, translation_candidates)) + [longest_partial_overlap])  # type: ignore
        return set(translation_candidates)
