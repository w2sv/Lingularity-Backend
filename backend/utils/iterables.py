from itertools import islice, tee, zip_longest
from typing import Iterable, Sequence, TypeVar


T = TypeVar('T')


def none_stripped(iterable: Iterable[T]) -> list[T]:
    return list(filter(lambda el: el is not None, iterable))


def intersection(sets: Iterable[set[T]]) -> set[T]:
    return set.intersection(*sets)


def windowed(iterable: Iterable[T], n: int) -> Iterable[tuple[T]]:
    return zip(*(islice(vert_iterable, i, None) for i, vert_iterable in enumerate(tee(iterable, n))))


def longest_value(iterable: Iterable[T]) -> T:
    return next(iter(sorted(iterable, key=len, reverse=True)))


def length_parity(*iterable) -> bool:
    return contains_unique_value(map(len, iterable))


def unzip(nested_list: Iterable[Iterable[T]]):
    return zip(*nested_list)


def unzip_longest(nested_list: Iterable[Iterable[T]]):
    return zip_longest(*nested_list)


def comprises_index(sequence: Sequence[T], index: int) -> bool:
    return index <= len(sequence) - 1


def contains_unique_value(iterable: Iterable[T]) -> bool:
    return len(set(iterable)) == 1
