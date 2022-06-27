from __future__ import annotations

from itertools import zip_longest
from typing import Iterable, Sequence, TypeVar


T = TypeVar('T')


def none_stripped(iterable: Iterable[T]) -> list[T]:
    return list(filter(lambda el: el is not None, iterable))


def intersection(sets: Iterable[set[T]]) -> set[T]:
    return set.intersection(*sets)


def longest_value(iterable: Iterable[T]) -> T:
    return next(iter(sorted(iterable, key=len, reverse=True)))  # type: ignore


def length_parity(*iterable) -> bool:
    return contains_unique_value(map(len, iterable))


def unzip_longest(nested_list: Iterable[Iterable[T]]):
    return zip_longest(*nested_list)


def comprises_index(sequence: Sequence[T], index: int) -> bool:
    return index <= len(sequence) - 1


def contains_unique_value(iterable: Iterable[T]) -> bool:
    return unique_contained_value(iterable) is not None


def unique_contained_value(iterable: Iterable[T]) -> T | None:
    unique_values = set(iterable)
    if len(unique_values) == 1:
        return next(iter(unique_values))
    else:
        return None
