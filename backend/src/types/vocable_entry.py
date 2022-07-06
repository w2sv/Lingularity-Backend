from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import TypeAlias

from backend.src.utils.date import n_days_ago


@dataclass
class VocableEntry:
    @classmethod
    def new(cls, vocable: str, translation: str):
        return cls(
            vocable,
            translation,
            0,
            0,
            None
        )

    vocable: str
    translation: str
    times_faced: int
    score: float
    last_faced_date: str | None

    @property
    def the_stripped_meaning(self):
        return self.translation.lstrip('the ')

    @property
    def is_new(self) -> bool:
        return self.last_faced_date is None

    def alter(self, new_vocable: str, new_meaning: str):
        self.vocable = new_vocable
        self.translation = new_meaning
        self.times_faced = 0
        self.score = 0
        self.last_faced_date = None

    def update_post_training_encounter(self, increment: float):
        self.score += increment
        self.times_faced += 1


def is_perfected(entry: VocableEntry) -> bool:
    if not entry.times_faced:
        return False
    assert entry.last_faced_date is not None
    return entry.score >= 5 and n_days_ago(entry.last_faced_date) < 50


VocableEntries: TypeAlias = list[VocableEntry]
