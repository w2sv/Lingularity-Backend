import os
import random
from typing import List

import pytest

from backend.data_paths import SENTENCE_DATA_DIR_PATH
from backend.trainers.base import Corpus
from backend.utils import strings
import backend.utils.strings.modification


# ----------------
# Basic
# ----------------
def _random_language() -> str:
    return random.choice(list(filter(lambda language_candidate: not language_candidate.startswith('.'), os.listdir(SENTENCE_DATA_DIR_PATH)))).split('.')[0]


@pytest.mark.parametrize('language', [
    (_random_language()),
    (_random_language()),
    (_random_language()),
    (_random_language()),
    (_random_language())
])
def test_reading_in(language):
    sentence_data = Corpus(language)

    for column in [sentence_data.english_sentences, sentence_data.foreign_language_sentences]:
        assert all(map(lambda character: not strings.contains_unicode(character), column.comprising_characters))


@pytest.mark.parametrize('train_english', [
    True,
    False
])
def test_language_assignment(train_english):
    sentence_data = Corpus('Czech', train_english=train_english)
    assert sentence_data.foreign_language_sentences[0] == 'Ahoj!'


# ----------------
# Quote Stripping
# ----------------
@pytest.mark.parametrize('language,stripped_bilateral_quotes', [
    ('Italian', [
        '"Dang Me"',
        '"Chug-A-Lug"',
        '"Jingle Bells"',
        "You Don't Want My Love",
        '"In the Summer Time"',
        '"password"',
        '"Jailhouse Rock"'
    ]),
    ('German', [
        '"Star Wars"',
        '"Tatoeba"',
        '"hipster"',
        '"Jingle Bells"'])
])
def test_bilaterally_present_quote_stripping(language, stripped_bilateral_quotes):
    sentence_data: Corpus = Corpus('Italian')
    sentence_data.strip_bilaterally_present_quotes()

    assert _bilaterally_present_strings(sentence_data, query_strings=stripped_bilateral_quotes, special_character_removed=True) == []


def _bilaterally_present_strings(
        sentence_data: Corpus,
        query_strings: List[str],
        special_character_removed: bool) -> List[str]:

    bilaterally_present_strings = []

    for sentence_pair in sentence_data:
        if special_character_removed:
            sentence_pair = list(map(backend.utils.strings.modification.strip_special_characters, sentence_pair))

        for query_string in query_strings:
            if query_string in sentence_pair[0] and query_string in sentence_pair[1]:
                bilaterally_present_strings.append(query_string)
                query_strings.remove(query_string)

    return bilaterally_present_strings


# def find_sentences_comprising_string_bilaterally(sentence_data: Corpus, string: str) -> List[str]:
#     sentences = []
#
#     for english_sentence, foreign_language_sentence in sentence_data._zipped_sentence_iterator:
#         if string in english_sentence and string in foreign_language_sentence:
#             sentences.append(' - '.join([english_sentence, foreign_language_sentence]))
#
#     return sentences


# ----------------
# Columns
# ----------------
@pytest.mark.parametrize('language,expected', [
    ('French', True),
    ('Spanish', True),
    ('Croatian', True),
    ('Japanese', False),
    ('Russian', False),
    ('Arabic', False),
    ('Serbian', False)
])
def test_employs_latin_script(language, expected):
    assert Corpus(language).foreign_language_sentences.uses_latin_script == expected


@pytest.mark.parametrize('language,tokens,expected', [
    ('German', ["c'est-à-dire"], False),
    ('French', ['Tom', 'Mary'], True),
    ('Italian', ['faccia', 'prigione', 'abbraccerà'], True),
    ('Korean', ['고마워', '잡아'], True)
])
def test_comprises_tokens(language, tokens, expected):
    assert Corpus(language).foreign_language_sentences.comprises_tokens(query_tokens=tokens) == expected


# ----------------
# Default Forename Translation Deduction
# ----------------
# @pytest.mark.parametrize('language,expected', [
#     ('French', [{'Tom', 'Toma', 'Tomas', 'Tome'}, ['Jean', 'Johan', 'John'], ['Maria', 'Marion', 'Mary'], ['Alice']]),
#     ('Danish', [['Rom', 'Thomas', 'Toms'], ['John', 'Johns'], ['Maria', 'Mary', 'Marys'], ['Alice']]),
#     ('Japanese', [['トム'], ['はジョン', 'ジョン'], ['してしまった', 'って伝えた', 'てあげて', 'には', 'るなんて', 'れていた', 'メアリー', '会うつもり'], []],),
#     ('Basque', [['Tomek', 'Tomem', 'Tomen', 'Tomeri', 'Tomi'], ['Johnekin'], ['Maria', 'Marik', 'Mary', 'Maryk', 'Maryri'], []])
# ])
# def test_deduce_default_forenames_translations(language, expected):
#     assert list(map(sorted, Corpus(language).deduce_forename_translations())) == expected
