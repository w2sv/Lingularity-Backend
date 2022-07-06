from __future__ import annotations

from typing import Type

from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from .client_base import MongoDBClientBase


def connect_database_client(server_selection_timeout=1_000) -> Type[ConfigurationError] | Type[ServerSelectionTimeoutError] | None:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        MongoDBClientBase.launch_cluster(server_selection_timeout=server_selection_timeout)
        MongoDBClientBase.assert_connection()
        return None
    except (ConfigurationError, ServerSelectionTimeoutError) as error:
        return type(error)
