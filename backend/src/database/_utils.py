ID = '_id'
UNIQUE_ID_FILTER = {ID: 'unique'}


def id_popped(document: dict) -> dict:
    document.pop(ID)
    return document