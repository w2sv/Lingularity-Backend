from typing import Callable

from backend.types.corpus import Corpus
from . import diction_expansion, random, simple


SentenceDataFilter = Callable[[Corpus, str], Corpus]
