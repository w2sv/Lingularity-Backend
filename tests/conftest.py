import pytest

from backend.database import connect_database_client, UserMongoDBClient


MONGODB_TEST_USER = 'janek'
MONGODB_TEST_LANGUAGE = 'Italian'


@pytest.fixture(scope='module', autouse=True)
def launch_database_client():
    connect_database_client(server_selection_timeout=2_000)
    UserMongoDBClient(MONGODB_TEST_USER, MONGODB_TEST_LANGUAGE)


@pytest.fixture
def user_mongo_client() -> UserMongoDBClient:
    return UserMongoDBClient.instance()