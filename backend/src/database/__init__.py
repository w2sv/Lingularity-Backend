from __future__ import annotations

from typing import Type

from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from backend.src.database.mongo_client import Client


def connect_database_client(server_selection_timeout=1_000) -> Type[ConfigurationError] | Type[ServerSelectionTimeoutError] | None:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        client = Client(server_selection_timeout=server_selection_timeout)
        client.assert_connection()
        return None
    except (ConfigurationError, ServerSelectionTimeoutError) as error:
        return type(error)
