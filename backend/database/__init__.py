from __future__ import annotations

from pathlib import Path
from typing import Iterator, Type

from monostate import MonoState
import pymongo
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError

from backend.utils import date
from backend.utils.io import load_config
from .document_types import (
    LastSessionStatistics,
    TrainingChronic,
    VocableData
)
from backend.metadata.string_resources import string_resources


# TODO: change vocable data keywords in database, user collection names


VocableEntryDictRepr = dict[str, VocableData]


def _client_endpoint(host: str, user: str, password: str) -> str:
    """ Employing srv endpoint """

    return f'mongodb+srv://{user}:{password}@{host}'


def instantiate_database_client(server_selection_timeout=1_000) -> Type[ConfigurationError] | Type[ServerSelectionTimeoutError] | None:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        MongoDBClient(server_selection_timeout=server_selection_timeout).assert_connection()
    except (ConfigurationError, ServerSelectionTimeoutError) as error:
        return type(error)
    return None


class MongoDBClient(MonoState):
    def __init__(self, server_selection_timeout=1_000):
        super().__init__(instance_kwarg_name='mongodb_client')

        self.user: str | None = None
        self.language: str | None = None

        credentials = load_config(Path(__file__).parent / 'credentials.ini')

        self._cluster: pymongo.MongoClient = pymongo.MongoClient(
            _client_endpoint(
                host=credentials['host'],
                user=credentials['user'],
                password=credentials['password']
            ),
            serverSelectionTimeoutMS=server_selection_timeout
        )

    def assert_connection(self):
        """ Triggers errors.ServerSelectionTimeoutError in case of its
            foundation being present """

        self.query_password('janek')

    @property
    def user_set(self) -> bool:
        return self.user is not None

    # --------------------
    # User transcendent
    # --------------------
    @property
    def mail_addresses(self) -> Iterator[str]:
        return (self._cluster[user_name]['general'].find_one(filter={'_id': 'unique'})['emailAddress'] for user_name in self.usernames)  # type: ignore

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses

    @property
    def usernames(self) -> list[str]:
        """ Equals databases """

        return self._cluster.list_database_names()

    # --------------------
    # User specific
    # --------------------
    @property
    def user_data_base(self) -> Database:
        assert self.user is not None
        return self._cluster[self.user]

    def remove_user(self):
        assert self.user is not None
        self._cluster.drop_database(self.user)

    def remove_language_data(self, language: str):
        _filter = {'_id': language}

        self.vocabulary_collection.delete_one(filter=_filter)
        self.training_chronic_collection.delete_one(filter=_filter)
        self.language_metadata_collection.delete_one(filter=_filter)

    # ------------------
    # Collections
    # ------------------
    @staticmethod
    def _get_ids(collection: pymongo.collection.Collection) -> list:
        return list(collection.find().distinct('_id'))

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

        return self.user_data_base['general']

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

    def query_password(self, username: str) -> str:
        self.user = username
        password = self.general_collection.find_one({'_id': 'unique'})['password']  # type: ignore
        self.user = None
        return password

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

        return self.user_data_base['vocabulary']

    def query_vocabulary_possessing_languages(self) -> set[str]:
        return set(self._get_ids(self.vocabulary_collection))

    def query_vocabulary(self) -> Iterator[tuple[str, VocableData]]:
        vocable_entries = self.vocabulary_collection.find_one(self.language)
        # assert vocable_entries is not None
        vocable_entries.pop('_id')  # type: ignore
        return iter(vocable_entries.items())  # type: ignore

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

        return self.user_data_base['training_chronic']

    def insert_dummy_entry(self, language: str):
        """ In order to persist language after selection however without having
            actually conducted any training actions on it yet """

        self.training_chronic_collection.update_one(
            filter={'_id': language},
            update={'$set': {f'{str(date.today)}': None}},
            upsert=True
        )

    def query_languages(self) -> list[str]:
        return self._get_ids(self.training_chronic_collection)

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

        return self.user_data_base['language_metadata']

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
