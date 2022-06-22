from itertools import starmap
from typing import List

from backend.database import MongoDBClient
from backend.trainers.vocable_trainer import VocableEntry, VocableTrainerBackend


def get_vocable_entries() -> List[VocableEntry]:
    return list(starmap(VocableEntry, MongoDBClient.instance().query_vocabulary()))


def test_find_paraphrases():
    EXPECTED = {'next to': ['di fianco', 'accanto a'], 'face': ['la faccia', 'il viso']}

    assert VocableTrainerBackend._find_paraphrases(get_vocable_entries()) == EXPECTED
