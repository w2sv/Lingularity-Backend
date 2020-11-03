import logging
from pathlib import Path
from .version import __version__


_BACKEND_DATA_PATH = f'{Path(__file__).parent}/backend/data'

SENTENCE_DATA_PATH = f'{_BACKEND_DATA_PATH}/sentence-data'
TOKEN_MAPS_PATH = f'{_BACKEND_DATA_PATH}/token-maps'
META_DATA_PATH = f'{_BACKEND_DATA_PATH}/meta-data'


def sentence_data_path(language: str) -> str:
    return f'{SENTENCE_DATA_PATH}/{language}.txt'


# enable logging
logging.basicConfig(filename='logging.txt', level=logging.INFO)
