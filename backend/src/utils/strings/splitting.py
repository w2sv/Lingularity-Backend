from __future__ import annotations

import re
from typing import Iterable

from backend.src.utils.strings._re_utils import join_to_pattern


def split_at_uppercase(string: str) -> list[str]:
    """
    >>> split_at_uppercase("EisgekuehlterBomelunder")
    ['Eisgekuehlter', 'Bomelunder'] """

    return re.findall('[A-Z][a-z]*', string)


def split_multiple(string: str, delimiters: Iterable[str]) -> list[str]:
    """
    >>> split_multiple('wildly,unreasonable:yet,lit!?af', delimiters=list(',:!?'))
    ['wildly', 'unreasonable', 'yet', 'lit', '', 'af'] """

    return join_to_pattern(delimiters).split(string)