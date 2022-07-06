import pytest

from tests.conftest import initialize_user_mongo_client, MONGODB_TEST_LANGUAGE, MONGODB_TEST_USER


def test_instantiation(user_mongo_client):
    assert user_mongo_client.user == MONGODB_TEST_USER
    assert user_mongo_client.language == MONGODB_TEST_LANGUAGE


def test_vocabulary_collection(user_mongo_client):
    assert user_mongo_client.vocabulary_collection.vocabulary_possessing_languages() == {'Spanish', 'French', 'Hungarian', 'Khasi', 'Afrikaans', 'Italian'}

    assert user_mongo_client.vocabulary_collection.database.name == MONGODB_TEST_USER
    assert user_mongo_client.vocabulary_collection.language == MONGODB_TEST_LANGUAGE

    assert user_mongo_client.vocabulary_collection.name == 'vocabulary'
    assert user_mongo_client.vocabulary_collection.full_name == f'{MONGODB_TEST_USER}.vocabulary'


def test_user_mongo_client_attribute_reflection_in_collection(user_mongo_client):
    user_mongo_client.user = 'other user'
    user_mongo_client.language = 'other language'

    assert user_mongo_client.vocabulary_collection.language == user_mongo_client.language
    assert user_mongo_client.vocabulary_collection.user == user_mongo_client.user


@pytest.fixture(autouse=True)
def reset_user_mongo_client():
    yield
    initialize_user_mongo_client()