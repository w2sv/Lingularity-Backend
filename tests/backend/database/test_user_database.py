from tests.conftest import MONGODB_TEST_LANGUAGE, MONGODB_TEST_USER


def test_instantiation(user_database):
    assert user_database.user == MONGODB_TEST_USER
    assert user_database.language == MONGODB_TEST_LANGUAGE


def test_vocabulary_collection(user_database):
    assert user_database.vocabulary_collection.vocabulary_possessing_languages() == {'Spanish', 'French', 'Hungarian', 'Khasi', 'Afrikaans', 'Italian'}

    assert user_database.vocabulary_collection.database.name == MONGODB_TEST_USER
    assert user_database.vocabulary_collection.language == MONGODB_TEST_LANGUAGE

    assert user_database.vocabulary_collection.name == 'vocabulary'
    assert user_database.vocabulary_collection.full_name == f'{MONGODB_TEST_USER}.vocabulary'


def test_user_mongo_client_attribute_reflection_in_collection(user_database):
    user_database.language = 'other language'

    assert user_database.vocabulary_collection.language == user_database.language