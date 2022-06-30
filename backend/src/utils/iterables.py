from __future__ import annotations

from itertools import zip_longest
from typing import Iterable, Sequence, TypeVar


T = TypeVar('T')


def none_stripped(iterable: Iterable[T]) -> list[T]:
    """
    >>> none_stripped([None, 4, 'a', None, None])
    [4, 'a'] """

    return list(filter(lambda el: el is not None, iterable))


def intersection(sets: Iterable[set[T]]) -> set[T]:
    """
    >>> intersection([{1, 5, 8, 3}, {1, 3, 98, 34}, {2, 22, 3}])
    {3}
    >>> intersection([{11, 22}, {33, 11, 55}, {12}])
    set() """

    return set.intersection(*sets)


def longest_value(iterable: Iterable[T]) -> T:
    """
    >>> longest_value(['', 'aa', 'tfff', 'dd', 'ghhhhj'])
    'ghhhhj' """

    return next(iter(sorted(iterable, key=len, reverse=True)))  # type: ignore


def length_parity(*iterable) -> bool:
    """
    >>> length_parity([None] * 4, [7] * 4)
    True
    >>> length_parity([None] * 4, [7] * 3)
    False """

    return contains_unique_value(map(len, iterable))


def unzip_longest(nested_list: Iterable[Iterable[T]]):
    return zip_longest(*nested_list)


def comprises_index(sequence: Sequence[T], index: int) -> bool:
    """
    >>> comprises_index(list(range(9)), index=9)
    False
    >>> comprises_index(list(range(9)), index=8)
    True """

    return index <= len(sequence) - 1


def contains_unique_value(iterable: Iterable[T]) -> bool:
    """
    >>> contains_unique_value(range(3))
    False
    >>> contains_unique_value([3] * 5)
    True """

    return unique_contained_value(iterable) is not None


def unique_contained_value(iterable: Iterable[T]) -> T | None:
    """
    >>> unique_contained_value([3] * 5)
    3
    >>> repr(unique_contained_value(range(2)))
    'None' """

    unique_values = set(iterable)
    if len(unique_values) == 1:
        return next(iter(unique_values))
    else:
        return None
