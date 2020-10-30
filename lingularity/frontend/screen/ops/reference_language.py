from typing import List

from lingularity.backend.database import MongoDBClient
from lingularity.backend.utils import string_resources
from lingularity.frontend.utils import input_resolution, output


def get(eligible_languages: List[str]) -> str:
    selection = query()

    if not selection:
        output.erase_lines(2)

        eligible_languages.remove(string_resources.ENGLISH)
        selection = input_resolution.query_relentlessly(f'{output.SELECTION_QUERY_OUTPUT_OFFSET}Select reference language: ', options=eligible_languages)

        MongoDBClient.get_instance().set_reference_language(reference_language=selection)

    return selection


def query():
    return MongoDBClient.get_instance().query_reference_language()
