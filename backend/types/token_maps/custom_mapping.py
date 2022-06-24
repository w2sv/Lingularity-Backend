from abc import ABC
from typing import Mapping

from backend.paths import TOKEN_MAPS_DIR_PATH
from backend.utils import io, strings


class CustomMapping(Mapping, ABC):
    @classmethod
    def data_file_name(cls) -> str:
        """ Returns:
                lowercase, dash-joined class name without 'token' """

        return '-'.join(map(lambda string: string.lower(), strings.split_at_uppercase(cls.__name__)[1:]))

    @classmethod
    def _data(cls, language: str, create: bool):
        return {} if create else cls._load_data(language=language)

    @classmethod
    def _load_data(cls, language: str):
        return io.load_pickle(file_path=TOKEN_MAPS_DIR_PATH / language / cls.data_file_name())

    @property
    def data(self):
        return {**self}