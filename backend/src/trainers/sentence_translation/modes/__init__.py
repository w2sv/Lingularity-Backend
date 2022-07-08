from typing import Callable

from typing_extensions import TypeAlias

from backend.src.types.bilingual_corpus import BilingualCorpus
from . import diction_expansion, random, simple


SentenceDataFilter: TypeAlias = Callable[[BilingualCorpus, str], BilingualCorpus]
