from typing import Set, Iterable, Any, List, Tuple, Sequence, Optional, Iterator, Generator, Callable
from itertools import tee, islice, zip_longest


def none_stripped(iterable: Iterable[Any]) -> List[Any]:
    return list(filter(lambda el: el is not None, iterable))


def intersection(sets: Iterable[Set[Any]]) -> Set[Any]:
    return set.intersection(*sets)


def windowed(iterable: Iterable[Any], n: int) -> Iterable[Tuple[Any]]:
    return zip(*(islice(vert_iterable, i, None) for i, vert_iterable in enumerate(tee(iterable, n))))


def longest_value(iterable: Iterable[Any]) -> Any:
    return sorted(iterable, key=len, reverse=True)[0]


def unzip(nested_list: Iterable[Iterable[Any]]):
    return zip(*nested_list)


def unzip_longest(nested_list: Iterable[Iterable[Any]]):
    return zip_longest(*nested_list)


def contains_index(sequence: Sequence[Any], index: int) -> bool:
    return index <= len(sequence) - 1


def contains_singular_unique_value(iterable: Iterable[Any]) -> bool:
    return len(set(iterable)) == 1


def return_value_capturing_generator(generator: Callable[..., Iterator[Any]]):
    class WrapperClass:
        def __init__(self, *args, **kwargs):
            self.generator: Iterator[Any] = generator(*args, **kwargs)
            self.return_value: Optional[Any] = None

        def __iter__(self):
            self.return_value = yield from self.generator

    return WrapperClass
