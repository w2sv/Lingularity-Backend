import pytest

from backend.src.trainers import VocableTrainerBackend


@pytest.fixture
def vocable_entries(user_database):
    return user_database.vocabulary_collection.entries()


def test_find_paraphrases(vocable_entries):
    assert VocableTrainerBackend._find_paraphrases(vocable_entries) == {
        'cool': ['figo', 'gergo'],
        'face': ['la faccia', 'il viso'],
        'next to': ['di fianco', 'accanto a'],
        'o annoy, to bother': ['dare fastidio', 'infastidiscere'],
        'unknown': ['lo sconosciuto', "l'ignoto"]
    }