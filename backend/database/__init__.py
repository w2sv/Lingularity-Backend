from __future__ import annotations

import os
from abc import ABC
from pathlib import Path
from typing import Iterator, Type

from monostate import MonoState
import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from backend.string_resources import string_resources
from backend.utils import date
from backend.utils.io import load_config
from .document_types import (
    LastSessionStatistics,
    TrainingChronic,
    VocableData
)


# TODO: change vocable data keywords in database, user collection names


VocableEntryDictRepr = dict[str, VocableData]


def connect_database_client(server_selection_timeout=1_000) -> Type[ConfigurationError] | Type[ServerSelectionTimeoutError] | None:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        _MongoDBClient.launch_cluster(server_selection_timeout=server_selection_timeout)
        _MongoDBClient.assert_connection()
    except (ConfigurationError, ServerSelectionTimeoutError) as error:
        return type(error)
    return None


def _collection_ids(collection: pymongo.collection.Collection) -> list:
    return list(collection.find().distinct('_id'))


class _MongoDBClient(MonoState, ABC):
    _cluster: MongoClient

    @classmethod
    def launch_cluster(cls, server_selection_timeout=1_500):
        cls._cluster = pymongo.MongoClient(
            host=cls._client_endpoint(),
            serverSelectionTimeoutMS=server_selection_timeout
        )

    @staticmethod
    def _client_endpoint() -> str:
        """ Uses srv endpoint """

        template = 'mongodb+srv://{}:{}@{}'

        if (credentials_fp := Path(__file__).parent / 'credentials.ini').exists():
            credentials = load_config(credentials_fp)
            return template.format(
                credentials['user'],
                credentials['password'],
                credentials['host'],
            )
        return template.format(
            os.environ['MONGODB_USER'],
            os.environ['MONGODB_PASSWORD'],
            os.environ['MONGODB_HOST'],
        )

    @classmethod
    def assert_connection(cls):
        """ Triggers errors.ServerSelectionTimeoutError in case of its
            foundation being present """

        cls._cluster.server_info()


class UserTranscendentMongoDBClient(_MongoDBClient):
    def __init__(self):
        super().__init__('user_transcendent_mongodb')

    @property
    def usernames(self) -> list[str]:
        return self._cluster.list_database_names()

    @property
    def mail_addresses(self) -> Iterator[str]:
        return (self._cluster[username]['general'].find_one(filter={'_id': 'unique'})['emailAddress'] for username in self.usernames)  # type: ignore

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses


class UserMongoDBClient(_MongoDBClient):
    def __init__(self, user: str, language: str):
        super().__init__('user_mongo_client')

        self.user = user
        self.language = language

    @property
    def data_base(self) -> Database:
        return self._cluster[self.user]

    def remove_user(self):
        self._cluster.drop_database(self.user)

    def remove_language_data(self, language: str):
        _filter = {'_id': language}

        self.vocabulary_collection.delete_one(filter=_filter)
        self.training_chronic_collection.delete_one(filter=_filter)
        self.language_metadata_collection.delete_one(filter=_filter)

    # ------------------
    # Collections
    # ------------------

    # ------------------
    # .General
    # ------------------
    @property
    def general_collection(self) -> pymongo.collection.Collection:
        """ {_id: 'unique',
             emaiLAddress: email_address,
             password: password,
             lastSession: {trainer: trainer,
                           nFacedItems: n_faced_items,
                           date: date,
                           language: language}} """

        return self.data_base['general']

    def initialize_user(self, user: str, email_address: str, password: str):
        self.user = user
        self.general_collection.insert_one({'_id': 'unique',
                                            'emailAddress': email_address,
                                            'password': password})

    def update_last_session_statistics(self, trainer: str, faced_items: int):
        self.general_collection.update_one(
            filter={'_id': 'unique'},
            update={'$set': {'lastSession': {'trainer': trainer,
                                             'nFacedItems': faced_items,
                                             'date': str(date.today),
                                             'language': self.language}}},
            upsert=True
        )

    def query_password(self) -> str:
        return self.general_collection.find_one({'_id': 'unique'})['password']  # type: ignore

    def query_last_session_statistics(self) -> LastSessionStatistics | None:
        try:
            return self.general_collection.find_one({'_id': 'unique'})['lastSession']  # type: ignore
        except KeyError:
            return None

    # ------------------
    # .Vocabulary
    # ------------------
    @property
    def vocabulary_collection(self) -> pymongo.collection.Collection:
        """ {'_id': language,
             $target_language_token: {t: translation_field
                                      tf: times_faced
                                      s: score
                                      lfd: last_faced_date}} """

        return self.data_base['vocabulary']

    def query_vocabulary_possessing_languages(self) -> set[str]:
        return set(_collection_ids(self.vocabulary_collection))

    def query_vocabulary(self) -> Iterator[tuple[str, VocableData]]:
        vocable_entries = self.vocabulary_collection.find_one(self.language)
        assert vocable_entries is not None
        vocable_entries.pop('_id')
        return iter(vocable_entries.items())

    def insert_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.vocabulary_collection.update_one(
            filter={'_id': self.language},
            update={'$set': vocable_entry},
            upsert=True
        )

    def delete_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.vocabulary_collection.update_one(
            filter={'_id': self.language},
            update={'$unset': vocable_entry}
        )

    def update_vocable_entry(self, vocable: str, new_score: float):
        self.vocabulary_collection.find_one_and_update(
            filter={'_id': self.language, vocable: {'$exists': True}},
            update={'$inc': {f'{vocable}.tf': 1},
                    '$set': {f'{vocable}.lfd': str(date.today),
                             f'{vocable}.s': new_score}},
            upsert=False
        )

    def alter_vocable_entry(self, old_vocable: str, altered_vocable_entry: VocableEntryDictRepr):
        # delete old sub document corresponding to old_vocable regardless of whether the vocable,
        # that is the sub document key has changed
        self.vocabulary_collection.find_one_and_update(
            filter={'_id': self.language},
            update={'$unset': {old_vocable: 1}}
        )

        self.insert_vocable_entry(altered_vocable_entry)

    # ------------------
    # .Training Chronic
    # ------------------
    @property
    def training_chronic_collection(self) -> pymongo.collection.Collection:
        """ {_id: language,
             $date: {$trainer_abbreviation: n_faced_items}} """

        return self.data_base['training_chronic']

    def insert_dummy_entry(self, language: str):
        """ In order to persist language after selection however without having
            actually conducted any training actions on it yet """

        self.training_chronic_collection.update_one(
            filter={'_id': language},
            update={'$set': {f'{str(date.today)}': None}},
            upsert=True
        )

    def query_languages(self) -> list[str]:
        return _collection_ids(self.training_chronic_collection)

    def inject_session_statistics(self, trainer_abbreviation: str, n_faced_items: int):
        self.training_chronic_collection.update_one(
            filter={'_id': self.language},
            update={'$inc': {f'{str(date.today)}.{trainer_abbreviation}': n_faced_items}},
            upsert=True
        )

    def query_training_chronic(self) -> TrainingChronic:
        training_chronic = next(iter(self.training_chronic_collection.find({'_id': self.language})))
        training_chronic.pop('_id')
        return training_chronic

    # ------------------
    # .Language Metadata
    # ------------------
    @property
    def language_metadata_collection(self) -> pymongo.collection.Collection:
        """ {_id: $language,
            accent: {$language_variety: {playbackSpeed: float
                                          use: bool}}
            ttsEnabled: bool} """

        return self.data_base['language_metadata']

    # ------------------
    # ..language accent usage
    # ------------------
    def set_language_variety_usage(self, variety_identifier: str, value: bool):
        self.language_metadata_collection.update_one(filter={'_id': self.language},
                                                     update={'$set': {f'accent.{variety_identifier}.use': value}},
                                                     upsert=True)

    def query_language_variety(self) -> str | None:
        """ assumes existence of varietyIdentifier sub dict in case of
            existence of language related collection """

        if (language_metadata := self.language_metadata_collection.find_one(filter={'_id': self.language})) is None:
            return None

        elif variety_2_usage := language_metadata.get('accent'):
            for identifier, value_dict in variety_2_usage.items():
                if value_dict['use']:
                    return identifier

        return None

    # ------------------
    # ..playback speed
    # ------------------
    def set_playback_speed(self, variety: str, playback_speed: float):
        self.language_metadata_collection.update_one(filter={'_id': self.language},
                                                     update={'$set': {f'accent.{variety}.playbackSpeed': playback_speed}},
                                                     upsert=True)

    def query_playback_speed(self, variety: str) -> float | None:
        try:
            return self.language_metadata_collection.find_one(filter={'_id': self.language})['accent'][variety]['playbackSpeed']  # type: ignore
        except (AttributeError, KeyError, TypeError):
            return None

    # ------------------
    # ..tts enablement
    # ------------------
    def set_tts_enablement(self, value: bool):
        self.language_metadata_collection.update_one(filter={'_id': self.language},
                                                     update={'$set': {
                                                        f'ttsEnabled': value}},
                                                     upsert=True)

    def query_tts_enablement(self):
        try:
            return self.language_metadata_collection.find_one(filter={'_id': self.language}).get('ttsEnabled')  # type: ignore
        except AttributeError:
            return None

    # ------------------
    # ..english reference language
    # ------------------
    def set_reference_language(self, reference_language: str):
        self.language_metadata_collection.update_one(filter={'_id': string_resources['english']},
                                                     update={'$set': {
                                                         f'referenceLanguage': reference_language}},
                                                     upsert=True)

    def query_reference_language(self) -> str | None:
        try:
            return self.language_metadata_collection.find_one(filter={'_id': string_resources['english']})['referenceLanguage']  # type: ignore
        except TypeError:
            return None
