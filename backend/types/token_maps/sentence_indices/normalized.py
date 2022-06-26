from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Iterator, TypeVar

from nltk import SnowballStemmer
from spacy import Language
from spacy.tokens import Doc, Token

from backend.ops.normalizing import lemmatizing
from backend.ops.normalizing.lemmatizing import spacy_models
from backend.types.token_maps.sentence_indices import Token2ComprisingSentenceIndices
from backend.utils.strings.extraction import meaningful_types
from backend.utils.strings.transformation import special_characters_stripped


_Token = TypeVar('_Token', Token, str)


class NormalizedToken2SentenceIndicesMap(Generic[_Token], Token2ComprisingSentenceIndices, ABC):
    def best_possibly_normalized_meaningful_types(self, sentence: str) -> set[str]:
        return set(self._normalize(self._types(sentence)))

    @abstractmethod
    def _types(self, text: str) -> set[_Token]:
        pass

    @abstractmethod
    def _normalize(self, types: Iterable[_Token]) -> Iterator[str]:
        pass


class StemSentenceIndicesMap(NormalizedToken2SentenceIndicesMap[str]):
    @staticmethod
    def is_available_for(language: str) -> bool:
        return language.lower() in SnowballStemmer.languages

    def __init__(self, data: dict | None, language: str, load_normalizer=True):
        super().__init__(data)

        self._stem: Callable[[str], str] | None = SnowballStemmer(language.lower()).stem if load_normalizer else None

    def _types(self, text: str) -> set[str]:
        return meaningful_types(text=text, apostrophe_splitting=True)

    def _normalize(self, types: Iterable[str]) -> Iterator[str]:
        assert self._stem is not None
        return map(self._stem, types)

    def comprising_sentence_indices(self, vocable: str) -> list[int] | None:
        length_sorted_stems = self._normalize(types=self._length_sorted_meaningful_types(vocable))
        return self._find_best_fit_sentence_indices(list(length_sorted_stems))


class LemmaSentenceIndicesMap(NormalizedToken2SentenceIndicesMap[Token]):
    _IGNORE_POS_TYPES = {'DET', 'PROPN', 'SYM', 'PUNCT', 'X', 'PART'}

    @staticmethod
    def is_available_for(language: str) -> bool:
        return language in spacy_models.LANGUAGE_2_MODEL_IDENTIFIERS.keys()

    def __init__(self, data: dict | None, language: str, load_normalizer=True):
        super().__init__(data)

        self._model: Language | None = lemmatizing.load_model(language) if load_normalizer else None

    def best_possibly_normalized_types_with_pos(self, sentence: str) -> set[tuple[str, str]]:
        filtered_tokens = self._types(special_characters_stripped(string=sentence))
        return set(map(lambda token: (token.lemma_, token.pos_), filtered_tokens))

    def _normalize(self, types: Iterable[Token]) -> Iterator[str]:
        return map(lambda _type: _type.lemma_, types)

    def _types(self, text: str) -> set[Token]:
        assert self._model is not None
        return set(self._filter_tokens(self._model(text)))

    def _filter_tokens(self, tokens: Doc) -> Iterator[Token]:
        return filter(lambda token: token.pos_ not in self._IGNORE_POS_TYPES, tokens)

    def comprising_sentence_indices(self, vocable: str) -> list[int] | None:
        REMOVE_POS_TYPES = {'DET', 'PROPN', 'SYM'}

        types = self._types(vocable)

        # remove types of REMOVE_POS_TYPE if types not solely comprised of them
        if len((pos_set := set((token.pos_ for token in types))).intersection(REMOVE_POS_TYPES)) != len(pos_set):
            types = set(filter(lambda token: token.pos_ not in REMOVE_POS_TYPES, types))

        pos_value_sorted_lemmas = [token.lemma_ for token in sorted(types, key=lambda t: lemmatizing.POS_VALUES.get(t.pos_, lemmatizing.PosValue.Null).value)]
        return self._find_best_fit_sentence_indices(relevance_sorted_types=pos_value_sorted_lemmas)
