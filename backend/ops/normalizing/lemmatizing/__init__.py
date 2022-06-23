""" https://spacy.io/models """


from enum import auto, Enum

import spacy

from backend.ops.normalizing.lemmatizing.spacy_models import model_name


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

def load_model(language: str) -> spacy.Language:
    print('Loading model...')
    return spacy.load(model_name(language=language))