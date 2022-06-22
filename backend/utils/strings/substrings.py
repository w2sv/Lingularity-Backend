from itertools import chain
from typing import Iterable, Iterator, Optional

from backend.utils import iterables


def continuous_substrings(string: str, lengths: Optional[Iterable[int]] = None, min_length=2) -> Iterator[str]:
    """
        Args:
            string: string to extract substrings from
            lengths: Iterable of desired substring lengths,
                may contain lengths > len(string) which will be automatically ignored
            min_length: of researched continuous substring

        Returns:
            Iterator of entirety of continuous substrings of min length comprised by string
            sorted with respect to their lengths

        >>> list(continuous_substrings('path'))
        ['pa', 'at', 'th', 'pat', 'ath', 'path'] """

    if lengths is None:
        lengths = range(min_length, len(string) + 1)
    else:
        lengths = filter(lambda val: val >= min_length, lengths)

    return map(''.join, chain.from_iterable(map(lambda length: iterables.windowed(string, length), lengths)))


def start_including_substrings(string: str) -> Iterator[str]:
    """
    >>> list(start_including_substrings('path'))
    ['p', 'pa', 'pat', 'path'] """

    for i in range(1, len(string) + 1):
        yield string[:i]
