""" https://spacy.io/models """


from enum import Enum, auto
from typing import Any

import spacy


# ---------------
# POS Values
# ---------------
class PosValue(Enum):
    Null = 0
    Low = auto()
    Medium = auto()
    High = auto()


POS_VALUES = {
    'NOUN': PosValue.High, 'VERB': PosValue.High, 'ADJ': PosValue.High, 'ADV': PosValue.High,
    'NUM': PosValue.Medium,
    'AUX': PosValue.Low, 'ADP': PosValue.Low, 'PRON': PosValue.Low
}


# ---------------
# Model Name Assembly/Loading
# ---------------
Model = Any


def load_model(language: str) -> Model:
    print('Loading model...')
    return spacy.load(_model_name(language=language))


def _model_name(language: str, model_size='sm') -> str:
    return f'{LANGUAGE_2_MODEL_IDENTIFIERS[language][0]}_core_{LANGUAGE_2_MODEL_IDENTIFIERS[language][1]}_{model_size}'


_WEB, _NEWS = 'web', 'news'


LANGUAGE_2_MODEL_IDENTIFIERS = {
    'Chinese': ['zh', _WEB],
    'Danish': ['da', _NEWS],
    'Dutch': ['nl', _NEWS],
    'English': ['en', _WEB],
    'French': ['fr', _NEWS],
    'German': ['de', _NEWS],
    'Greek': ['el', _NEWS],
    'Italian': ['it', _NEWS],
    'Japanese': ['ja', _NEWS],
    'Lithuanian': ['lt', _NEWS],
    'Norwegian': ['nb', _NEWS],
    'Polish': ['pl', _NEWS],
    'Portuguese': ['pt', _NEWS],
    'Romanian': ['ro', _NEWS],
    'Spanish': ['es', _NEWS]
}


AVAILABLE_LANGUAGES = set(LANGUAGE_2_MODEL_IDENTIFIERS.keys())
