from backend.metadata.paths import DATA_DIR_PATH
from backend.utils.io import load_config


string_resources = load_config(DATA_DIR_PATH / 'string-resources.ini')