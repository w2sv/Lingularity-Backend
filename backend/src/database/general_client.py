from __future__ import annotations

from typing import Iterator

from pymongo.database import Database

from backend.src.database import MongoDBClientBase
from backend.src.database._utils import UNIQUE_ID_FILTER


class GeneralMongoDBClient(MongoDBClientBase):
    def __init__(self):
        super().__init__(instance_kwarg_name='general_mongo_client')

    @property
    def _credentials_db(self) -> Database:
        return self._cluster['CREDENTIALS']

    def usernames(self) -> list[str]:
        return self._credentials_db.list_collection_names()

    def initialize_user(self, username: str, email_address: str, password: str):
        self._credentials_db[username].insert_one(
            UNIQUE_ID_FILTER | {
                'emailAddress': email_address,
                'password': password
            }
        )

    def remove_user(self, username: str):
        self._cluster.drop_database(username)
        self._credentials_db.drop_collection(username)

    def query_password(self, username: str) -> str:
        return self._credentials_db[username].find_one(filter=UNIQUE_ID_FILTER)['password']  # type: ignore

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses()

    def mail_addresses(self) -> Iterator[str]:
        return (self._credentials_db[collection_name].find_one(filter=UNIQUE_ID_FILTER)['emailAddress'] for collection_name in self._credentials_db.list_collection_names())