from typing import Optional, Tuple, List, Any, Iterator, Set, Dict

import pymongo
from pymongo import errors


from backend.utils import state_sharing, date, string_resources
from .document_types import (
    LastSessionStatistics,
    TrainingChronic,
    VocableData
)


# TODO: change vocable data keywords in database, user collection names


VocableEntryDictRepr = Dict[str, VocableData]


def _client_endpoint(host: str, user: str, password: str) -> str:
    """ Employing srv endpoint """

    return f'mongodb+srv://{user}:{password}@{host}'


def instantiate_client(server_selection_timeout: float = 1_000) -> Optional[errors.PyMongoError]:
    """ Returns:
            instantiation_error: errors.PyMongoError in case of existence, otherwise None """

    try:
        MongoDBClient(server_selection_timeout=server_selection_timeout).assert_connection()
    except (errors.ConfigurationError, errors.ServerSelectionTimeoutError) as error:
        return type(error)
    return None


class MongoDBClient(state_sharing.MonoStatePossessor):
    def __init__(self, server_selection_timeout: float):
        super().__init__()

        self._user: Optional[str] = None
        self._language: Optional[str] = None

        self._cluster: pymongo.MongoClient = pymongo.MongoClient(
            _client_endpoint(
                host='cluster0.zthtl.mongodb.net/admin?retryWrites=true&w=majority',
                user='sickdude69',
                password='clusterpassword'),
            serverSelectionTimeoutMS=server_selection_timeout
        )

    def assert_connection(self):
        """ Triggers errors.ServerSelectionTimeoutError in case of its
            foundation being present """

        self.query_password('janek')

    @property
    def user(self) -> Optional[str]:
        return self._user

    @user.setter
    def user(self, value: str):
        self._user = value

    @property
    def user_set(self) -> bool:
        return self.user is not None

    @property
    def language(self) -> Optional[str]:
        return self._language

    @language.setter
    def language(self, value: str):
        self._language = value

    # --------------------
    # User transcendent
    # --------------------
    @property
    def mail_addresses(self) -> Iterator[str]:
        return (self._cluster[user_name]['general'].find_one(filter={'_id': 'unique'})['emailAddress'] for user_name in self.usernames)

    def mail_address_taken(self, mail_address: str) -> bool:
        return mail_address in self.mail_addresses

    @property
    def usernames(self) -> List[str]:
        """ Equals databases """

        return self._cluster.list_database_names()

    # --------------------
    # User specific
    # --------------------
    @property
    def user_data_base(self) -> pymongo.collection.Collection:
        return self._cluster[self._user]

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
    @staticmethod
    def _get_ids(collection: pymongo.collection.Collection) -> List[Any]:
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
                                             'language': self._language}}},
            upsert=True
        )

    def query_password(self, username: str) -> str:
        self._user = username
        password = self.general_collection.find_one({'_id': 'unique'})['password']
        self._user = None
        return password

    def query_last_session_statistics(self) -> Optional[LastSessionStatistics]:
        try:
            return self.general_collection.find_one({'_id': 'unique'})['lastSession']
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

    def query_vocabulary_possessing_languages(self) -> Set[str]:
        return set(self._get_ids(self.vocabulary_collection))

    def query_vocabulary(self) -> Iterator[Tuple[str, VocableData]]:
        vocable_entries = self.vocabulary_collection.find_one(self._language)
        vocable_entries.pop('_id')
        return iter(vocable_entries.items())

    def insert_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.vocabulary_collection.update_one(
            filter={'_id': self._language},
            update={'$set': vocable_entry},
            upsert=True
        )

    def delete_vocable_entry(self, vocable_entry: VocableEntryDictRepr):
        self.vocabulary_collection.update_one(
            filter={'_id': self._language},
            update={'$unset': vocable_entry}
        )

    def update_vocable_entry(self, vocable: str, new_score: float):
        self.vocabulary_collection.find_one_and_update(
            filter={'_id': self._language, vocable: {'$exists': True}},
            update={'$inc': {f'{vocable}.tf': 1},
                    '$set': {f'{vocable}.lfd': str(date.today),
                             f'{vocable}.s': new_score}},
            upsert=False
        )

    def alter_vocable_entry(self, old_vocable: str, altered_vocable_entry: VocableEntryDictRepr):
        # delete old sub document corresponding to old_vocable regardless of whether the vocable,
        # that is the sub document key has changed
        self.vocabulary_collection.find_one_and_update(
            filter={'_id': self._language},
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

    def query_languages(self) -> List[str]:
        return self._get_ids(self.training_chronic_collection)

    def inject_session_statistics(self, trainer_abbreviation: str, n_faced_items: int):
        self.training_chronic_collection.update_one(
            filter={'_id': self._language},
            update={'$inc': {f'{str(date.today)}.{trainer_abbreviation}': n_faced_items}},
            upsert=True
        )

    def query_training_chronic(self) -> TrainingChronic:
        training_chronic = next(iter(self.training_chronic_collection.find({'_id': self._language})))
        training_chronic.pop('_id')
        return training_chronic

    # ------------------
    # .Language Metadata
    # ------------------
    @property
    def language_metadata_collection(self) -> pymongo.collection.Collection:
        """ {_id: $language,
            variety: {$language_variety: {playbackSpeed: float
                                          use: bool}}
            ttsEnabled: bool} """

        return self.user_data_base['language_metadata']

    # ------------------
    # ..language variety usage
    # ------------------
    def set_language_variety_usage(self, variety_identifier: str, value: bool):
        self.language_metadata_collection.update_one(filter={'_id': self._language},
                                                     update={'$set': {f'variety.{variety_identifier}.use': value}},
                                                     upsert=True)

    def query_language_variety(self) -> Optional[str]:
        """ assumes existence of varietyIdentifier sub dict in case of
            existence of language related collection """

        if (language_metadata := self.language_metadata_collection.find_one(filter={'_id': self._language})) is None:
            return None

        elif variety_2_usage := language_metadata.get('variety'):
            for identifier, value_dict in variety_2_usage.items():
                if value_dict['use']:
                    return identifier

        return None

    # ------------------
    # ..playback speed
    # ------------------
    def set_playback_speed(self, variety: str, playback_speed: float):
        self.language_metadata_collection.update_one(filter={'_id': self._language},
                                                     update={'$set': {f'variety.{variety}.playbackSpeed': playback_speed}},
                                                     upsert=True)

    def query_playback_speed(self, variety: str) -> Optional[float]:
        try:
            return self.language_metadata_collection.find_one(filter={'_id': self._language})['variety'][variety]['playbackSpeed']
        except (AttributeError, KeyError, TypeError):
            return None

    # ------------------
    # ..tts enablement
    # ------------------
    def set_tts_enablement(self, value: bool):
        self.language_metadata_collection.update_one(filter={'_id': self._language},
                                                     update={'$set': {
                                                        f'ttsEnabled': value}},
                                                     upsert=True)

    def query_tts_enablement(self):
        try:
            return self.language_metadata_collection.find_one(filter={'_id': self._language}).get('ttsEnabled')
        except AttributeError:
            return None

    # ------------------
    # ..english reference language
    # ------------------
    def set_reference_language(self, reference_language: str):
        self.language_metadata_collection.update_one(filter={'_id': string_resources.ENGLISH},
                                                     update={'$set': {
                                                         f'referenceLanguage': reference_language}},
                                                     upsert=True)

    def query_reference_language(self) -> Optional[str]:
        try:
            return self.language_metadata_collection.find_one(filter={'_id': string_resources.ENGLISH})['referenceLanguage']
        except TypeError:
            return None
