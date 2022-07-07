from __future__ import annotations

from itertools import zip_longest
from typing import Iterable, Sequence, Sized, TypeVar


_T = TypeVar('_T')


def none_stripped(iterable: Iterable[_T]) -> list[_T]:
    """
    >>> none_stripped([None, 4, 'a', None, None, False])
    [4, 'a', False] """

    return list(filter(lambda el: el is not None, iterable))


def intersection(sets: Iterable[set[_T]]) -> set[_T]:
    """
    >>> intersection([{1, 5, 8, 3}, {1, 3, 98, 34}, {2, 22, 3}])
    {3}
    >>> intersection([{11, 22}, {33, 11, 55}, {12}])
    set() """

    return set.intersection(*sets)


_T_Sized = TypeVar('_T_Sized', bound=Sized)


def longest_value(iterable: Iterable[_T_Sized]) -> _T_Sized:
    """
    >>> longest_value(['', 'aa', 'tfff', 'dd', 'ghhhhj'])
    'ghhhhj' """

    return max(iterable, key=len)


def length_parity(*sequence: Sequence) -> bool:
    """
    >>> length_parity([''] * 4, [''] * 4)
    True
    >>> length_parity([''] * 4, [''] * 3)
    False """

    return contains_unique_value(map(len, sequence))


def unzip_longest(nested_list: Iterable[Iterable[_T]]):
    return zip_longest(*nested_list)


def comprises_index(sequence: Sequence[_T], index: int) -> bool:
    """
    >>> comprises_index(list(range(9)), index=9)
    False
    >>> comprises_index(list(range(9)), index=8)
    True """

    return index <= len(sequence) - 1


def contains_unique_value(iterable: Iterable[_T]) -> bool:
    """
    >>> contains_unique_value(range(3))
    False
    >>> contains_unique_value([3] * 5)
    True """

    return unique_contained_value(iterable) is not None


def unique_contained_value(iterable: Iterable[_T]) -> _T | None:
    """
    >>> unique_contained_value([3] * 5)
    3
    >>> repr(unique_contained_value(range(2)))
    'None' """

    unique_values = set(iterable)
    if len(unique_values) == 1:
        return next(iter(unique_values))
    return None
