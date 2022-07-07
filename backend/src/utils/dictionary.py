from typing import TypeVar


_K = TypeVar('_K')
_V = TypeVar('_V')


def items_reversed(d: dict[_K, _V]) -> dict[_V, _K]:
    """
    >>> items_reversed({1: 'a', 2: 'b'})
    {'a': 1, 'b': 2} """

    return {v: k for k, v in d.items()}