from __future__ import annotations

from abc import ABC
import os
from pathlib import Path

from monostate import MonoState
import pymongo
from pymongo import MongoClient

from backend.src.utils.io import load_config


class AbstractMongoDBClient(MonoState, ABC):
    _cluster: MongoClient

    @classmethod
    def launch_cluster(cls, server_selection_timeout=1_500):
        cls._cluster = pymongo.MongoClient(
            host=cls._client_endpoint(),
            serverSelectionTimeoutMS=server_selection_timeout
        )

    @staticmethod
    def _client_endpoint() -> str:
        """ Uses srv endpoint """

        template = 'mongodb+srv://{}:{}@{}'

        if (credentials_fp := Path(__file__).parent / 'credentials.ini').exists():
            credentials = load_config(credentials_fp)
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

    @classmethod
    def assert_connection(cls):
        """ Triggers errors.ServerSelectionTimeoutError in case of its
            foundation being present """

        cls._cluster.server_info()