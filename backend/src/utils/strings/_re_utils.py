import re
from typing import Iterable


def join_to_pattern(strings: Iterable[str]) -> re.Pattern:
    return re.compile('|'.join(map(re.escape, strings)))