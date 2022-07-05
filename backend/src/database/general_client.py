from __future__ import annotations

from typing import Iterator

from pymongo.collection import Collection

from backend.src.database import AbstractMongoDBClient
from backend.src.database._utils import UNIQUE_ID_FILTER


class GeneralMongoDBClient(AbstractMongoDBClient):
    def __init__(self):
        super().__init__(instance_kwarg_name='general_mongo_client')

    @property
    def usernames(self) -> list[str]:
        return self._cluster.list_database_names()

    def _general_user_collection(self, username: str) -> Collection:
        return self._cluster[username]['general']

    def query_password(self, username: str) -> str:
        return self._general_user_collection(username).find_one(UNIQUE_ID_FILTER)['password']  # type: ignore

    @property
    def mail_addresses(self) -> Iterator[str]:
        return (self._general_user_collection(username).find_one(UNIQUE_ID_FILTER)['emailAddress'] for username in self.usernames)  # type: ignore

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses

    def initialize_user(self, username: str, email_address: str, password: str):
        self._general_user_collection(username).insert_one(
            UNIQUE_ID_FILTER | {
                'emailAddress': email_address,
                'password': password
            }
        )