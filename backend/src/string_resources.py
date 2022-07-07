from backend.src.paths import RESOURCES_DIR_PATH
from backend.src.utils.io import load_config_section


string_resources = load_config_section(RESOURCES_DIR_PATH / 'strings.ini')