from typing import Callable

from backend.src.types.bilingual_corpus import BilingualCorpus
from . import diction_expansion, random, simple


SentenceDataFilter = Callable[[BilingualCorpus, str], BilingualCorpus]
