from typing import List
from itertools import starmap

from backend.database import MongoDBClient
from backend.trainers.components import VocableEntry


mongodb = MongoDBClient()
mongodb.user = 'janek'
mongodb.language = 'Italian'


def get_vocable_entries() -> List[VocableEntry]:
    return list(starmap(VocableEntry, MongoDBClient.get_instance().query_vocabulary()))
