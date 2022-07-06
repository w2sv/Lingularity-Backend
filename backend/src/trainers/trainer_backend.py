from __future__ import annotations

from abc import ABC, abstractmethod
import random
from typing import Generic, Iterator, TypeVar

import numpy as np

from backend.src.components.forename_convertor import ForenameConvertor
from backend.src.database.user_database import UserDatabase
from backend.src.string_resources import string_resources
from backend.src.types.bilingual_corpus import BilingualCorpus, SentencePair
from backend.src.types.vocable_entry import VocableEntries, VocableEntry


_TrainingItem = TypeVar('_TrainingItem', SentencePair, VocableEntry)
_TrainingItems = TypeVar('_TrainingItems', BilingualCorpus, VocableEntries)


class TrainerBackend(ABC, Generic[_TrainingItem, _TrainingItems]):
    @UserDatabase.receiver
    def __init__(self, non_english_language: str, train_english: bool, user_database: UserDatabase):
        self._non_english_language = non_english_language
        self._train_english = train_english

        user_database.language = self.language
        self.user_database = user_database

        self._item_iterator: Iterator[_TrainingItem]
        self.n_training_items: int

        self.forename_converter: ForenameConvertor | None = self._get_forename_converter()

    def _get_forename_converter(self) -> ForenameConvertor | None:
        if ForenameConvertor.available_for(self._non_english_language):
            return ForenameConvertor(self._non_english_language, train_english=self._train_english)
        return None

    @property
    def language(self) -> str:
        return [self._non_english_language, string_resources['english']][self._train_english]

    # ----------------
    # Pre Training
    # ----------------
    @abstractmethod
    def set_item_iterator(self):
        """ Sets item iterator, n training items """

    def _set_item_iterator(self, items: _TrainingItems):
        self.n_training_items = len(items)
        self._item_iterator = self._get_item_iterator(items)

    @staticmethod
    def _get_item_iterator(items: _TrainingItems) -> Iterator[_TrainingItem]:
        if isinstance(items, np.ndarray):
            np.random.shuffle(items)
        else:
            random.shuffle(items)

        return iter(items)  # type: ignore

    def _get_sentence_data(self) -> BilingualCorpus:
        return BilingualCorpus(self._non_english_language, self._train_english)

    # -----------------
    # Training
    # -----------------
    def get_training_item(self) -> _TrainingItem | None:
        """ Returns:
                 None in case of depleted iterator """

        assert self._item_iterator is not None
        return next(self._item_iterator, None)

    # -----------------
    # Post Training
    # -----------------
    def enter_session_statistics_into_database(self, n_trained_items: int):
        update_args = (self.shortform, n_trained_items)

        self.user_database.general_collection.upsert_last_session_statistics(*update_args)
        self.user_database.training_chronic_collection.upsert_session_statistics(*update_args)

    @property
    def shortform(self) -> str:
        return self.__class__.__name__[0].lower()
