from backend.src.paths import RESOURCES_DIR_PATH
from backend.src.utils.io import load_config


string_resources = load_config(RESOURCES_DIR_PATH / 'strings.ini')