import pytest

from backend.database import MongoDBClient

MONGODB_TEST_USER = 'janek'
MONGODB_TEST_LANGUAGE = 'Italian'


@pytest.fixture(scope='module', autouse=True)
def instantiate_database():
    mongodb = MongoDBClient(server_selection_timeout=2000)
    mongodb.user = MONGODB_TEST_USER
    mongodb.language = MONGODB_TEST_LANGUAGE


@pytest.fixture
def mongodb_instance() -> MongoDBClient:
    return MongoDBClient.instance()