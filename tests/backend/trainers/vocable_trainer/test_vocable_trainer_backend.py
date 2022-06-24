from itertools import starmap
from typing import List

import pytest

from backend.trainers.vocable_trainer import VocableEntry, VocableTrainerBackend


@pytest.fixture
def vocable_entries(mongodb_instance) -> List[VocableEntry]:
    print(mongodb_instance.user, mongodb_instance.language)
    return list(starmap(VocableEntry, mongodb_instance.query_vocabulary()))


def test_find_paraphrases(vocable_entries):
    assert VocableTrainerBackend._find_paraphrases(vocable_entries) == {
        'cool': ['figo', 'gergo'],
        'face': ['la faccia', 'il viso'],
        'next to': ['di fianco', 'accanto a'],
        'o annoy, to bother': ['dare fastidio', 'infastidiscere'],
        'unknown': ['lo sconosciuto', "l'ignoto"]
    }