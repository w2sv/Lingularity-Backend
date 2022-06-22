from backend import MongoDBClient


def test_instantiation():
    MongoDBClient()
    MongoDBClient.instance()