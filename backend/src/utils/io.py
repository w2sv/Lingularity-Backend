from configparser import ConfigParser, SectionProxy
import json
from mmap import ACCESS_READ, mmap
from pathlib import Path
import pickle
from typing import Any, Iterator, TypeVar


PathLike = TypeVar("PathLike", str, Path)


def read_mmapped(file_path: PathLike) -> Iterator[str]:
    with open(file_path, mode='r', encoding='utf-8') as file_obj:
        mmap_obj = mmap(file_obj.fileno(), length=0, access=ACCESS_READ)
        while line := mmap_obj.readline():  # type: ignore
            yield line.decode('utf-8')  # type: ignore


def write_json(data: dict, file_path: PathLike):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json(file_path: PathLike):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return json.load(f, strict=False)


def write_pickle(data: Any, file_path: PathLike):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(file_path: PathLike) -> Any:
    return pickle.load(open(file_path, 'rb'))


def load_config_section(file_path: PathLike) -> SectionProxy:
    config = ConfigParser()
    config.read(file_path)
    return config['DEFAULT']