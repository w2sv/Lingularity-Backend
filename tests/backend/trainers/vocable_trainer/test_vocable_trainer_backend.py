from itertools import starmap
from typing import List

import pytest

from backend.src.trainers import VocableTrainerBackend
from backend.src.types.vocable_entry import VocableEntry


@pytest.fixture
def vocable_entries(user_mongo_client) -> List[VocableEntry]:
    return list(starmap(VocableEntry, user_mongo_client.query_vocabulary()))


def test_find_paraphrases(vocable_entries):
    assert VocableTrainerBackend._find_paraphrases(vocable_entries) == {
        'cool': ['figo', 'gergo'],
        'face': ['la faccia', 'il viso'],
        'next to': ['di fianco', 'accanto a'],
        'o annoy, to bother': ['dare fastidio', 'infastidiscere'],
        'unknown': ['lo sconosciuto', "l'ignoto"]
    }