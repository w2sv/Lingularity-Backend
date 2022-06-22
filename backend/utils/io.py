from configparser import ConfigParser
import json
import os.path
from pathlib import Path
import pickle
from typing import Any, Dict, TypeVar


PathLike = TypeVar("PathLike", str, Path)


def write_json(data: Dict[Any, Any], file_path: str):
    with open(f'{file_path}.json', 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)


def load_json(file_path: str):
    with open(f'{file_path}.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def write_pickle(data: Any, file_path: str):
    with open(file_path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(file_path: str) -> Any:
    return pickle.load(open(file_path, 'rb'))


def load_config(file_path: PathLike) -> ConfigParser:
    if not os.path.exists(file_path):
        raise ValueError(f'{file_path} does not exist')

    config = ConfigParser()
    config.read(file_path)
    return config