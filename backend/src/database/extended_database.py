from __future__ import annotations

from abc import ABC
from typing import Iterator, NoReturn

from monostate import MonoState
from pymongo.collection import Collection
from pymongo.database import Database

from backend.src.database.mongo_client import Client


class ExtendedDatabase(Database, MonoState, ABC):
    @Client.receiver
    def __init__(self, name: str, client: Client):
        MonoState.__init__(self)
        Database.__init__(self, client=client, name=name)

    def __bool__(self) -> NoReturn:
        pass

    def collections(self) -> Iterator[Collection]:
        return (self[name] for name in self.list_collection_names())