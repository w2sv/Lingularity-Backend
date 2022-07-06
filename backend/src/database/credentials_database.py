from __future__ import annotations

from typing import Iterator

from backend.src.database._utils import UNIQUE_ID_FILTER
from backend.src.database.extended_database import ExtendedDatabase


class CredentialsDatabase(ExtendedDatabase):
    def __init__(self):
        super().__init__(name='CREDENTIALS')

    def usernames(self) -> list[str]:
        return self.list_collection_names()

    def initialize_user(self, username: str, email_address: str, password: str):
        self[username].insert_one(
            UNIQUE_ID_FILTER | {
                'emailAddress': email_address,
                'password': password
            }
        )

    def remove_user(self, username: str):
        self.client.drop_database(username)
        self.drop_collection(username)

    def query_password(self, username: str) -> str:
        return self[username].find_one(filter=UNIQUE_ID_FILTER)['password']  # type: ignore

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses()

    def mail_addresses(self) -> Iterator[str]:
        return (collection.find_one(filter=UNIQUE_ID_FILTER)['emailAddress'] for collection in self.collections())  # type: ignore