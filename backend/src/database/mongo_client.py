from __future__ import annotations

import os
from pathlib import Path

from monostate import MonoState
from pymongo import MongoClient

from backend.src.utils.io import load_config_section


class Client(MongoClient, MonoState):
    def __init__(self, server_selection_timeout: int):
        MonoState.__init__(self)
        MongoClient.__init__(
            self,
            host=self._client_endpoint(),
            serverSelectionTimeoutMS=server_selection_timeout
        )

    @staticmethod
    def _client_endpoint() -> str:
        """ Uses srv endpoint """

        template = 'mongodb+srv://{}:{}@{}'

        if (credentials_fp := Path(__file__).parent / 'credentials.ini').exists():
            credentials = load_config_section(credentials_fp)
            return template.format(
                credentials['user'],
                credentials['password'],
                credentials['host'],
            )
        return template.format(
            os.environ['MONGODB_USER'],
            os.environ['MONGODB_PASSWORD'],
            os.environ['MONGODB_HOST'],
        )

    def assert_connection(self):
        """ Triggers errors.ServerSelectionTimeoutError in case of its
            foundation being present """

        self.server_info()