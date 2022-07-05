from __future__ import annotations

from typing import Type

from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from .abstract_client import AbstractMongoDBClient
from .document_types import (
    LastSessionStatistics,
    TrainingChronic,
    VocableData
)


def connect_database_client(server_selection_timeout=1_000) -> Type[ConfigurationError] | Type[ServerSelectionTimeoutError] | None:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        AbstractMongoDBClient.launch_cluster(server_selection_timeout=server_selection_timeout)
        AbstractMongoDBClient.assert_connection()
    except (ConfigurationError, ServerSelectionTimeoutError) as error:
        return type(error)
