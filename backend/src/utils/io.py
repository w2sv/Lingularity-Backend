from configparser import ConfigParser, SectionProxy
import json
from pathlib import Path
import pickle
from typing import Any, TypeVar


PathLike = TypeVar("PathLike", str, Path)


def write_json(data: dict, file_path: PathLike):
    with open(file_path, 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)


def load_json(file_path: PathLike):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as read_file:
        return json.load(read_file, strict=False)


def write_pickle(data: Any, file_path: PathLike):
    with open(file_path, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(file_path: PathLike) -> Any:
    return pickle.load(open(file_path, 'rb'))


def load_config(file_path: PathLike) -> SectionProxy:
    config = ConfigParser()
    config.read(file_path)
    return config['DEFAULT']