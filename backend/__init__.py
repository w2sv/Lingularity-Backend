from backend.version import __version__
from backend.database import MongoDBClient, instantiate_client as instantiate_database_client

from backend import trainers
from backend import utils

from backend.utils import string_resources

from backend.ops.stemming import STEMMABLE_LANGUAGES
from backend.ops.google.text_to_speech import TTSABLE_LANGUAGES
from backend.utils.spacy import ELIGIBLE_LANGUAGES as LEMMATIZABLE_LANGUAGES
from backend.metadata import language_metadata
