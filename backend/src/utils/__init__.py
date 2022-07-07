from __future__ import annotations

from typing import TypeVar


_T = TypeVar('_T')


def either_or(value: _T | None, fallback: _T) -> _T:
    """ Returns:
            value if != None, else fallback """

    return value if value is not None else fallback
