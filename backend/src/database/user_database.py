from __future__ import annotations

from abc import ABC
from itertools import starmap
from typing import Iterator, TypedDict

from typing_extensions import TypeAlias

from backend.src.database._utils import ID, id_popped, UNIQUE_ID_FILTER
from backend.src.database.extended_collection import ExtendedCollection
from backend.src.database.extended_database import ExtendedDatabase
from backend.src.types.vocable_entry import VocableEntry
from backend.src.utils import date


class UserDatabase(ExtendedDatabase):
    def __init__(self, user: str, language: str):
        super().__init__(name=user)

        self.language = language

        self.vocabulary_collection = VocabularyCollection(self)
        self.training_chronic_collection = TrainingChronicCollection(self)
        self.language_metadata_collection = LanguageMetadataCollection(self)

        self._collections: list[_UserCollection] = [
            self.vocabulary_collection,
            self.training_chronic_collection,
            self.language_metadata_collection
        ]

    @property
    def user(self) -> str:
        return self.name

    def remove_language_related_documents(self):
        for collection in self._collections:
            collection.remove_language_related_documents()


class _UserCollection(ExtendedCollection, ABC):
    def __init__(self, database: UserDatabase):
        super().__init__(database=database)

        self._user_database = database

    @property
    def language(self) -> str:
        return self._user_database.language

    @property
    def user(self) -> str:
        return self._user_database.user

    def remove_language_related_documents(self):
        self.delete_one(filter=self._language_id_filter)

    @property
    def _language_id_filter(self) -> dict:
        return {ID: self.language}


_DOCUMENT_ACCESS_EXCEPTIONS = (KeyError, TypeError)


class _VocableDataCorpus(TypedDict):
    t: str
    tf: int
    s: float
    lfd: str | None


_VocableEntryDocument: TypeAlias = dict[str, _VocableDataCorpus]


class VocabularyCollection(_UserCollection):
    """ {'_id': language,
                 $target_language_token: {t: translation_field
                                          tf: times_faced
                                          s: score
                                          lfd: last_faced_date}} """

    @staticmethod
    def _entry_2_document(entry: VocableEntry) -> _VocableEntryDocument:
        return {
            entry.vocable: {
                't': entry.translation,
                'tf': entry.times_faced,
                's': entry.score,
                'lfd': entry.last_faced_date
            }
        }

    @staticmethod
    def _to_entry(vocable: str, entry_corpus: dict) -> VocableEntry:
        return VocableEntry(
            vocable=vocable,
            translation=entry_corpus['t'],
            times_faced=entry_corpus['tf'],
            score=entry_corpus['s'],
            last_faced_date=entry_corpus['lfd']
        )

    def vocabulary_possessing_languages(self) -> set[str]:
        return set(self._ids())

    def entries(self) -> Iterator[VocableEntry]:
        vocable_entry_document: dict | None = self.find_one(self.language)
        assert vocable_entry_document is not None
        vocable_entry_documents = id_popped(vocable_entry_document)
        return starmap(self._to_entry, vocable_entry_documents.items())

    def upsert_entry(self, entry: VocableEntry):
        self.update_one(
            filter=self._language_id_filter,
            update={'$set': self._entry_2_document(entry)},
            upsert=True
        )

    def delete_entry(self, entry: VocableEntry):
        self.update_one(
            filter=self._language_id_filter,
            update={'$unset': self._entry_2_document(entry)}
        )

    def update_vocable_entry(self, vocable: str, new_score: float):
        self.find_one_and_update(
            filter=self._language_id_filter | {vocable: {'$exists': True}},
            update={
                '$inc': {f'{vocable}.tf': 1},
                '$set': {
                    f'{vocable}.lfd': str(date.today()),
                    f'{vocable}.s': new_score
                }
            }
        )

    def alter_entry(self, old_vocable: str, altered_vocable_entry: VocableEntry):
        # delete old sub document corresponding to old_vocable regardless of whether the vocable,
        # that is the sub document key has changed
        self.find_one_and_update(
            filter=self._language_id_filter,
            update={'$unset': {old_vocable: 1}}
        )
        self.upsert_entry(altered_vocable_entry)


class TrainingChronicCollection(_UserCollection):
    """ {_id: language,
                 $date: {$trainer_shortform: n_faced_items}} """

    def upsert_last_session_statistics(self, trainer: str, faced_items: int):
        self.update_one(
            filter=UNIQUE_ID_FILTER,
            update={'$set': {'lastSession': {'trainer': trainer,
                                             'nFacedItems': faced_items,
                                             'date': str(date.today()),
                                             'language': self.language}}},
            upsert=True
        )

    def query_last_session_statistics(self) -> LastSessionStatistics | None:
        try:
            return self.find_one(UNIQUE_ID_FILTER)['lastSession']  # type: ignore
        except _DOCUMENT_ACCESS_EXCEPTIONS:
            return None

    def upsert_language_placeholder_document(self, language: str):
        """ In order to persist language after selection however without having
            actually conducted any training actions on it yet """

        self.update_one(
            filter={ID: language},
            update={'$set': {str(date.today()): None}},
            upsert=True
        )

    def languages(self) -> list[str]:
        return self._ids()

    def upsert_session_statistics(self, trainer_shortform: str, n_faced_items: int):
        self.update_one(
            filter=self._language_id_filter,
            update={'$inc': {f'{date.today()}.{trainer_shortform}': n_faced_items}},
            upsert=True
        )

    def training_chronic(self) -> TrainingChronic:
        document: dict | None = self.find_one(self._language_id_filter)
        assert document is not None
        return TrainingChronic(id_popped(document))


TrainingChronic = dict[str, dict[str, int]]


class LastSessionStatistics(TypedDict):
    trainer: str
    nFacedItems: int
    date: str
    language: str


class LanguageMetadataCollection(_UserCollection):
    """ {_id: $language,
                new_value: {$new_value: {playbackSpeed: float
                                              use: bool}}
                ttsEnabled: bool} """

    # ------------------
    # Accent
    # ------------------
    def upsert_accent(self, accent: str):
        self.language_metadata_collection.update_one(
            filter=self._language_id_filter,
            update={'$set': {'accent': accent}},
            upsert=True
        )

    def query_accent(self) -> str | None:
        """ assumes existence of varietyIdentifier sub dict in case of
            existence of language related collection """

        try:
            return self.find_one(filter=self._language_id_filter)['accent']  # type: ignore
        except _DOCUMENT_ACCESS_EXCEPTIONS:
            return None

    # ------------------
    # Playback Speed
    # ------------------
    def upsert_playback_speed(self, accent: str, playback_speed: float):
        self.update_one(
            filter=self._language_id_filter,
            update={'$set': {f'playbackSpeed.{accent}': playback_speed}},
            upsert=True
        )

    def query_playback_speed(self, accent: str) -> float | None:
        try:
            return self.find_one(filter=self._language_id_filter)['playbackSpeed'][accent]  # type: ignore
        except _DOCUMENT_ACCESS_EXCEPTIONS:
            return None

    # ------------------
    # Enablement
    # ------------------
    def upsert_tts_enablement(self, value: bool):
        self.update_one(
            filter=self._language_id_filter,
            update={
                '$set': {
                    'ttsEnabled': value
                }
            },
            upsert=True
        )

    def query_tts_enablement(self):
        try:
            return self.find_one(filter=self._language_id_filter)['ttsEnabled']  # type: ignore
        except _DOCUMENT_ACCESS_EXCEPTIONS:
            return None

    # ------------------
    # English Training
    # ------------------
    _ENGLISH_TRAINING_FILTER = {ID: 'englishTraining'}

    def upsert_reference_language(self, reference_language: str):
        self.update_one(
            filter=self._ENGLISH_TRAINING_FILTER,
            update={
                '$set': {
                    'referenceLanguage': reference_language
                }
            },
            upsert=True
        )

    def query_reference_language(self) -> str | None:
        try:
            return self.find_one(filter=self._ENGLISH_TRAINING_FILTER)['referenceLanguage']  # type: ignore
        except _DOCUMENT_ACCESS_EXCEPTIONS:
            return None