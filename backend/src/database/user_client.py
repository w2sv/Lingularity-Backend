from __future__ import annotations

from abc import ABC
from typing import Iterator

from pymongo.database import Database

from backend.src.database import AbstractMongoDBClient, LastSessionStatistics, TrainingChronic, VocableData
from backend.src.database._utils import ID, UNIQUE_ID_FILTER
from backend.src.string_resources import string_resources
from backend.src.types.vocable_entry import VocableEntryDictRepr
from backend.src.utils import date


class UserMongoDBClient(AbstractMongoDBClient):
    def __init__(self, user: str, language: str):
        super().__init__(instance_kwarg_name='user_mongo_client')

        self.user = user
        self.language = language

        database = self._cluster[user]
        self.vocabulary_collection = VocabularyCollection(database, 'vocabulary', self)
        self.general_collection = VocabularyCollection(database, 'general', self)
        self.training_chronic_collection = VocabularyCollection(database, 'training_chronic', self)
        self.language_metadata_collection = VocabularyCollection(database, 'language_metadata', self)

    def remove_user(self):
        self._cluster.drop_database(self.user)

    def remove_language_data(self, language: str):
        _filter = {ID: language}

        self.vocabulary_collection.delete_one(filter=_filter)
        self.training_chronic_collection.delete_one(filter=_filter)
        self.language_metadata_collection.delete_one(filter=_filter)


class AbstractCollection(ABC):
    def __init__(self, database: Database, name: str, user_mongo_client: UserMongoDBClient):
        self._collection = database[name]
        self._user_mongo_client = user_mongo_client

    def __getattr__(self, item):
        try:
            return getattr(self._collection, item)
        except AttributeError:
            return getattr(self._user_mongo_client, item)

    @property
    def _language_id_filter(self) -> dict:
        return {ID: self.language}

    def _ids(self) -> list:
        return list(self.find().distinct(ID))


class GeneralCollection(AbstractCollection):
    """ {_id: 'unique',
                 emaiLAddress: email_address,
                 password: password,
                 lastSession: {trainer: trainer,
                               nFacedItems: n_faced_items,
                               date: date,
                               language: language}} """

    def upsert_last_session_statistics(self, trainer: str, faced_items: int):
        self.update_one(
            filter=UNIQUE_ID_FILTER,
            update={'$set': {'lastSession': {'trainer': trainer,
                                             'nFacedItems': faced_items,
                                             'date': str(date.today),
                                             'language': self.language}}},
            upsert=True
        )

    def query_last_session_statistics(self) -> LastSessionStatistics | None:
        try:
            return self.find_one(UNIQUE_ID_FILTER)['lastSession']  # type: ignore
        except KeyError:
            return None


class VocabularyCollection(AbstractCollection):
    """ {'_id': language,
                 $target_language_token: {t: translation_field
                                          tf: times_faced
                                          s: score
                                          lfd: last_faced_date}} """

    def query_vocabulary_possessing_languages(self) -> set[str]:
        return set(self._ids())

    def query_vocabulary(self) -> Iterator[tuple[str, VocableData]]:
        vocable_entries: dict | None = self.find_one(self.language)
        assert vocable_entries is not None
        vocable_entries.pop(ID)
        return iter(vocable_entries.items())

    def upsert_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.update_one(
            filter=self._language_id_filter,
            update={'$set': vocable_entry},
            upsert=True
        )

    def delete_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.update_one(
            filter=self._language_id_filter,
            update={'$unset': vocable_entry}
        )

    def update_vocable_entry(self, vocable: str, new_score: float):
        self.find_one_and_update(
            filter=self._language_id_filter | {vocable: {'$exists': True}},
            update={
                '$inc': {f'{vocable}.tf': 1},
                '$set': {
                    f'{vocable}.lfd': str(date.today),
                    f'{vocable}.s': new_score
                }
            }
        )

    def alter_vocable_entry(self, old_vocable: str, altered_vocable_entry: VocableEntryDictRepr):
        # delete old sub document corresponding to old_vocable regardless of whether the vocable,
        # that is the sub document key has changed
        self.find_one_and_update(
            filter=self._language_id_filter,
            update={'$unset': {old_vocable: 1}}
        )

        self.upsert_vocable_entry(altered_vocable_entry)


class TrainingChronicCollection(AbstractCollection):
    """ {_id: language,
                 $date: {$trainer_abbreviation: n_faced_items}} """

    def insert_dummy_entry(self, language: str):
        """ In order to persist language after selection however without having
            actually conducted any training actions on it yet """

        self.update_one(
            filter={ID: language},
            update={'$set': {str(date.today): None}},
            upsert=True
        )

    def query_languages(self) -> list[str]:
        return self._ids()

    def inject_session_statistics(self, trainer_abbreviation: str, n_faced_items: int):
        self.update_one(
            filter=self._language_id_filter,
            update={'$inc': {f'{date.today}.{trainer_abbreviation}': n_faced_items}},
            upsert=True
        )

    def query_training_chronic(self) -> TrainingChronic:
        training_chronic = next(iter(self.find(self._language_id_filter)))
        training_chronic.pop('_id')
        return training_chronic


class LanguageMetadataCollection(AbstractCollection):
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
        except (KeyError, AttributeError, IndexError):
            return None

    # ------------------
    # Playback Speed
    # ------------------
    def upsert_playback_speed(self, accent: str, playback_speed: float):
        self.update_one(
            filter=self._language_id_filter,
            update={'$set': {f'accent.{accent}.playbackSpeed': playback_speed}},
            upsert=True
        )

    def query_playback_speed(self, accent: str) -> float | None:
        try:
            return self.find_one(filter=self._language_id_filter)['accent'][accent]['playbackSpeed']  # type: ignore
        except (AttributeError, KeyError, TypeError):
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
            return self.find_one(filter=self._language_id_filter).get('ttsEnabled')  # type: ignore
        except AttributeError:
            return None

    # ------------------
    # English Training
    # ------------------
    _ENGLISH_FILTER_ID = {ID: string_resources['english']}

    def set_reference_language(self, reference_language: str):
        self.update_one(
            filter=self._ENGLISH_FILTER_ID,
            update={
                '$set': {
                    f'referenceLanguage': reference_language
                }
            },
            upsert=True
        )

    def query_reference_language(self) -> str | None:
        try:
            return self.find_one(filter=self._ENGLISH_FILTER_ID)['referenceLanguage']  # type: ignore
        except TypeError:
            return None