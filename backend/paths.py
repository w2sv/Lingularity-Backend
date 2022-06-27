from pathlib import Path


_ROOT = Path(__file__).parent.parent

DATA_DIR_PATH = _ROOT / 'data'

CORPORA_DIR_PATH = DATA_DIR_PATH / 'corpora'
TOKEN_MAPS_DIR_PATH = DATA_DIR_PATH / 'token-maps'
META_DATA_DIR_PATH = DATA_DIR_PATH / 'meta-data'


def corpora_path(language: str) -> Path:
    return CORPORA_DIR_PATH / f'{language}.txt'


RESOURCES_DIR_PATH = _ROOT / 'resources'
