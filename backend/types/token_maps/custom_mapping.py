from abc import ABC
from collections.abc import Mapping

from backend.paths import TOKEN_MAPS_DIR_PATH
from backend.utils import io, strings


class CustomMapping(ABC, Mapping):
    @property
    def data_file_name(self) -> str:
        """ Returns:
                lowercase, dash-joined class name without 'token' """

        return '-'.join(map(lambda string: string.lower(), strings.split_at_uppercase(self.__class__.__name__)[1:]))

    def _data(self, language: str, create: bool):
        return {} if create else self._load_data(language=language)

    def _load_data(self, language: str):
        return io.load_pickle(file_path=TOKEN_MAPS_DIR_PATH / language / self.data_file_name)

    @property
    def data(self):
        return {**self}