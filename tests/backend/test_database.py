from tests.conftest import MONGODB_TEST_LANGUAGE, MONGODB_TEST_USER


def test_instantiation(user_mongo_client):
    assert user_mongo_client.user == MONGODB_TEST_USER
    assert user_mongo_client.language == MONGODB_TEST_LANGUAGE

