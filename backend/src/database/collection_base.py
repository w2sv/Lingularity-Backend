from __future__ import annotations

from abc import ABC

from pymongo.collection import Collection
from pymongo.database import Database

from backend.src.database._utils import ID
from backend.src.utils.strings.splitting import split_at_uppercase


class CollectionBase(Collection, ABC):
    def __init__(self, database: Database):
        super().__init__(
            database,
            name=self._name()
        )

    def _name(self) -> str:
        """ Returns:
                class name without trailing 'Collection', converted to snake case """

        return '_'.join(
            map(
                lambda token: token.lower(),
                split_at_uppercase(self.__class__.__name__)[:-1]
            )
        )

    def _ids(self) -> list:
        return list(self.find().distinct(ID))

    def __bool__(self):
        pass