from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TypeVar

from backend.src.paths import TOKEN_MAPS_DIR_PATH
from backend.src.utils import io
from backend.src.utils.strings.splitting import split_at_uppercase


VT = TypeVar('VT')


class TokenMap(defaultdict[str, VT], ABC):
    @classmethod
    def load(cls, language: str):
        return cls(cls._load_data(language), language=language)

    @staticmethod
    @abstractmethod
    def _factory():
        """  """

    def __init__(self, data: dict | None = None, *args, **kwargs):
        super().__init__(self._factory(), data or {})

    @classmethod
    def _load_data(cls, language: str):
        return io.load_pickle(file_path=TOKEN_MAPS_DIR_PATH / language / cls.data_file_name())

    @classmethod
    def data_file_name(cls) -> str:
        """ Returns:
                lowercase, dash-joined class name without 'token' """

        return '-'.join(map(lambda string: string.lower(), split_at_uppercase(cls.__name__)[1:]))

    @property
    def data(self):
        return {**self}