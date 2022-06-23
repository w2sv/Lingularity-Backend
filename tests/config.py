import pytest

from backend.database import MongoDBClient


@pytest.fixture(scope='session', autouse=True)
def instantiate_database():
    mongodb = MongoDBClient()
    mongodb.user = 'janek'
    mongodb.language = 'Italian'