from functools import lru_cache

import pytest

from backend.src.database import connect_database_client
from backend.src.database.user_database import UserDatabase
from backend.src.types.bilingual_corpus import BilingualCorpus


MONGODB_TEST_USER = 'janek'
MONGODB_TEST_LANGUAGE = 'Italian'


@pytest.fixture(scope='session', autouse=True)
def launch_database_client():
    connect_database_client(server_selection_timeout=2_000)


@pytest.fixture(autouse=True)
def instantiate_user_database():
    UserDatabase(MONGODB_TEST_USER, MONGODB_TEST_LANGUAGE)


@pytest.fixture
def user_database() -> UserDatabase:
    return UserDatabase.instance()


@lru_cache
def get_bilingual_corpus(language: str, train_english=False) -> BilingualCorpus:
    """ Cashes already instantiated corpora for reuse """

    return BilingualCorpus(language, train_english=train_english)