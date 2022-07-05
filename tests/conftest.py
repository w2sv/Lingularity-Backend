from functools import lru_cache

import pytest

from backend.src.database import connect_database_client
from backend.src.database.user_client import UserMongoDBClient
from backend.src.types.bilingual_corpus import BilingualCorpus


MONGODB_TEST_USER = 'janek'
MONGODB_TEST_LANGUAGE = 'Italian'


@pytest.fixture(scope='module', autouse=True)
def launch_database_client():
    connect_database_client(server_selection_timeout=2_000)
    UserMongoDBClient(MONGODB_TEST_USER, MONGODB_TEST_LANGUAGE)


@pytest.fixture
def user_mongo_client() -> UserMongoDBClient:
    return UserMongoDBClient.instance()


@lru_cache
def get_bilingual_corpus(language: str, train_english=False) -> BilingualCorpus:
    """ Cashes already instantiated corpora for reuse """

    return BilingualCorpus(language, train_english=train_english)