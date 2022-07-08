import datetime
from itertools import chain

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


def test_training_chronic_collection(user_database):
    language = 'Swedish'
    n_faced_items = 69
    trainer = 's'

    today_str = str(datetime.date.today())

    user_database.language = language
    user_database.training_chronic_collection.upsert_session_statistics(trainer, n_faced_items=n_faced_items)

    assert user_database.training_chronic_collection.last_session_statistics() == {'date': today_str, 'language': language, 'nFacedItems': n_faced_items, 'trainer': trainer}

    training_chronic = user_database.training_chronic_collection.training_chronic()
    assert isinstance(training_chronic, dict)
    assert len(training_chronic)
    entirety_of_unique_trainer_shortforms = set(chain.from_iterable(trainer_2_n_faced_items.keys() for trainer_2_n_faced_items in training_chronic.values()))
    assert not entirety_of_unique_trainer_shortforms - {'s', 'v'}
    assert not training_chronic[today_str][trainer] % n_faced_items
