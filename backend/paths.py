from pathlib import Path

from backend.utils.io import PathLike


DATA_DIR_PATH = Path(__file__).parent.parent / 'data'

SENTENCE_DATA_DIR_PATH = DATA_DIR_PATH / 'sentence-data'
TOKEN_MAPS_DIR_PATH = DATA_DIR_PATH / 'token-maps'
META_DATA_DIR_PATH = DATA_DIR_PATH / 'meta-data'


def sentence_data_path(language: str) -> PathLike:
    return SENTENCE_DATA_DIR_PATH / f'{language}.txt'  # type: ignore
