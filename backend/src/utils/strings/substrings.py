from __future__ import annotations

from typing import Iterator

from more_itertools import windowed


def continuous_substrings(string: str, lengths: Iterator[int] | None = None) -> Iterator[str]:
    """
        Args:
            string: string to extract substrings from
            lengths: Iterable of desired substring lengths,
                may contain lengths > len(string) which will be automatically ignored

        Returns:
            Iterator of entirety of continuous substrings of min length comprised by string
            sorted with respect to their lengths

        >>> list(continuous_substrings('path'))
        ['pa', 'at', 'th', 'pat', 'ath', 'path'] """

    if lengths is None:
        lengths = iter(range(2, len(string) + 1))
    try:
        yield from map(str().join, windowed(string, n=next(lengths), fillvalue=str()))
        yield from continuous_substrings(string, lengths=lengths)
    except StopIteration:
        pass


def start_including_substrings(string: str) -> Iterator[str]:
    """
    >>> list(start_including_substrings('path'))
    ['p', 'pa', 'pat', 'path'] """

    for i in range(1, len(string) + 1):
        yield string[:i]
