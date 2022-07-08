from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, TypeVar


_OptionalComponent = TypeVar('_OptionalComponent', bound='OptionalComponent')


class OptionalComponent(ABC):
    @classmethod
    def get_if_available_for(cls: Type[_OptionalComponent], language: str, *init_args, **init_kwargs) -> _OptionalComponent | None:
        if cls._available_for(language):
            return cls(language, *init_args, **init_kwargs)
        return None

    @abstractmethod
    def __init__(self, language: str, *args, **kwargs):
        """ """

    @staticmethod
    @abstractmethod
    def _available_for(language: str) -> bool:
        """  """