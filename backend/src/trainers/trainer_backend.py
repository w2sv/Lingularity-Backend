from __future__ import annotations

from abc import ABC, abstractmethod
import random
from typing import Callable, Generic, Iterator, TypeVar

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
        self.language = [non_english_language, string_resources['english']][train_english]
        user_database.language = self.language

        self._item_iterator: Iterator[_TrainingItem]
        self._get_bilingual_corpus: Callable[[], BilingualCorpus] = lambda: BilingualCorpus(non_english_language, train_english=train_english)
        self.n_training_items: int

        self.forename_converter: ForenameConvertor | None = ForenameConvertor.get_if_available_for(self.language, train_english=train_english)

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

    # -----------------
    # Training
    # -----------------
    def get_training_item(self) -> _TrainingItem | None:
        """ Returns:
                 None in case of depleted iterator """

        return next(self._item_iterator, None)
