from pathlib import Path


_ROOT = Path(__file__).parent.parent.parent

DATA_DIR_PATH = _ROOT / 'data'

CORPUS_DIR_PATH = DATA_DIR_PATH / 'corpora'
TOKEN_MAPS_DIR_PATH = DATA_DIR_PATH / 'token-maps'
META_DATA_DIR_PATH = DATA_DIR_PATH / 'meta-data'


def corpus_path(language: str) -> Path:
    return CORPUS_DIR_PATH / f'{language}.txt'


RESOURCES_DIR_PATH = _ROOT / 'resources'
