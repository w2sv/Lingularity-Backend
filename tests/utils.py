from typing import List
from itertools import starmap

from backend.database import MongoDBClient
from backend.trainers.components import VocableEntry


def get_mongodb_client() -> MongoDBClient:
    mongodb = MongoDBClient()
    mongodb.user = 'janek'
    mongodb.language = 'Italian'

    return mongodb


def get_vocable_entries() -> List[VocableEntry]:
    return list(starmap(VocableEntry, get_mongodb_client().query_vocabulary()))
