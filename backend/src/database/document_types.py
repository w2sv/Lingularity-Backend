from __future__ import annotations

from mypy_extensions import TypedDict


class LastSessionStatistics(TypedDict):
    trainer: str
    nFacedItems: int
    date: str
    language: str


TrainingChronic = dict[str, dict[str, int]]


class VocableDataCorpus(TypedDict):
    t: str
    tf: int
    s: float
    lfd: str | None