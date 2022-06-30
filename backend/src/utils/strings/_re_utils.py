import re
from re import Pattern
from typing import Iterable


def join_to_pattern(strings: Iterable[str]) -> Pattern:
    return re.compile('|'.join(map(re.escape, strings)))