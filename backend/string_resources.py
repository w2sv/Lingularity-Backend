from backend.paths import RESOURCES_DIR_PATH
from backend.utils.io import load_config


string_resources = load_config(RESOURCES_DIR_PATH / 'strings.ini')