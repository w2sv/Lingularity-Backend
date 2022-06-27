from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, Iterator, TypeVar

from nltk import SnowballStemmer
from spacy import Language
from spacy.tokens import Doc, Token as SpacyToken

from backend.ops import spacy_models
from backend.ops.spacy_models import POS
from backend.types.token_maps.sentence_indices import Token2ComprisingSentenceIndices
from backend.utils.strings.extraction import meaningful_types
from backend.utils.strings.transformation import special_characters_stripped


Token = TypeVar('Token', SpacyToken, str)


class NormalizedToken2SentenceIndicesMap(Generic[Token], Token2ComprisingSentenceIndices, ABC):
    def best_possibly_normalized_meaningful_types(self, sentence: str) -> set[str]:
        return set(self._normalize(self._types(sentence)))

    @abstractmethod
    def _types(self, text: str) -> set[Token]:
        pass

    @abstractmethod
    def _normalize(self, types: Iterable[Token]) -> Iterator[str]:
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


class LemmaSentenceIndicesMap(NormalizedToken2SentenceIndicesMap[SpacyToken]):
    _LOW_PERTINENCE = 1
    _MEDIUM_PERTINENCE = 2
    _HIGH_PERTINENCE = 3

    _POS_TAG_2_PERTINENCE = {
        POS.Noun: _HIGH_PERTINENCE,
        POS.Verb: _HIGH_PERTINENCE,
        POS.Adjective: _HIGH_PERTINENCE,
        POS.Adverb: _HIGH_PERTINENCE,

        POS.Number: _MEDIUM_PERTINENCE,

        POS.Auxiliary: _LOW_PERTINENCE,
        POS.Pronoun: _LOW_PERTINENCE,
        POS.ADP: _LOW_PERTINENCE
    }

    @staticmethod
    def is_available_for(language: str) -> bool:
        return language in spacy_models.LANGUAGE_2_MODEL_IDENTIFIERS.keys()

    def __init__(self, data: dict | None, language: str, load_normalizer=True):
        super().__init__(data)

        self._model: Language | None = spacy_models.load_model(language) if load_normalizer else None

    def best_possibly_normalized_types_with_pos(self, sentence: str) -> set[tuple[str, str]]:
        filtered_tokens = self._types(special_characters_stripped(string=sentence))
        return set(map(lambda token: (token.lemma_, token.pos_), filtered_tokens))

    def _normalize(self, types: Iterable[SpacyToken]) -> Iterator[str]:
        return map(lambda _type: _type.lemma_, types)

    def _types(self, text: str) -> set[SpacyToken]:
        assert self._model is not None
        return set(self._filter_tokens(self._model(text)))

    @staticmethod
    def _filter_tokens(tokens: Doc) -> Iterator[SpacyToken]:
        IGNORE_POS = {
            POS.Determinant,
            POS.ProperNoun,
            POS.Symbol,
            POS.Punctuation,
            POS.X,
            POS.Particle
        }

        return filter(lambda token: _pos(token) not in IGNORE_POS, tokens)

    def comprising_sentence_indices(self, vocable: str) -> list[int] | None:
        types = self._types(vocable)

        if pertinent_types := list(filter(lambda token: self._POS_TAG_2_PERTINENCE.get(_pos(token)) is not None, types)):
            pertinent_types.sort(key=lambda token: self._POS_TAG_2_PERTINENCE[_pos(token)])
            return self._find_best_fit_sentence_indices(relevance_sorted_types=_lemmas(pertinent_types))
        return self._find_best_fit_sentence_indices(relevance_sorted_types=sorted(_lemmas(types), key=len))


def _lemmas(tokens: Iterable[SpacyToken]) -> list[str]:
    return [token.lemma_ for token in tokens]

def _pos(token: SpacyToken) -> POS:
    return POS(token.pos_)