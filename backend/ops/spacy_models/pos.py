from enum import Enum


class POS(Enum):
    Noun = 'NOUN'
    Verb = 'VERB'
    Adjective = 'ADJ'
    Adverb = 'ADV'
    Number = 'NUM'
    Auxiliary = 'AUX'
    ADP = 'ADP'
    Pronoun = 'PRON'
    Symbol = 'SYM'
    ProperNoun = 'PROPN'
    Determinant = 'DET'
    Punctuation = 'PUNCT'
    X = 'X'
    Particle = 'PART'

    {'DET', 'PROPN', 'SYM', 'PUNCT', 'X', 'PART'}