""" https://spacy.io/models """


from enum import Enum, auto
from typing import Any

import spacy

from spacy_models import model_name


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
    return spacy.load(model_name(language=language))