import pytest

from backend.database import MongoDBClient


@pytest.fixture(scope='module', autouse=True)
def instantiate_database():
    mongodb = MongoDBClient()
    mongodb.user = 'janek'
    mongodb.language = 'Italian'

    yield


@pytest.fixture
def mongodb_instance() -> MongoDBClient:
    return MongoDBClient.instance()