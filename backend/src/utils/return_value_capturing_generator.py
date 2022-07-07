from __future__ import annotations

from typing import Any, Generator, Iterator, TypeVar


_T = TypeVar('_T')
_U = TypeVar('_U')


class ReturnValueCapturingGenerator:
    """ Reference: https://stackoverflow.com/a/34073559/12083276

    >>> def generator():
    ...     yield from range(3)
    ...     return 69
    >>> capturing = ReturnValueCapturingGenerator(generator())
    >>> list(capturing)
    [0, 1, 2]
    >>> capturing.value
    69 """

    def __init__(self, generator: Generator[_T, Any, _U]):
        self._generator: Iterator[Any] = generator
        self.value: _U | None = None

    def __iter__(self):
        self.value = yield from self._generator