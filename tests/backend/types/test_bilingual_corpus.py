import re
from typing import Iterator, List

import numpy as np
import pytest

from backend.trainers.base import BilingualCorpus
from backend.utils.strings.transformation import asciiized, special_characters_stripped, UNICODE_POINT_PATTERN
from tests.conftest import get_bilingual_corpus


def test_numpy_properties():
    bilingual_corpus = get_bilingual_corpus('Bulgarian', train_english=False)

    assert bilingual_corpus.shape == (15138, 2)
    assert isinstance(bilingual_corpus[0], np.ndarray)
    assert bilingual_corpus.dtype == np.dtype('<U262')

    assert not bilingual_corpus[0, 1].endswith('\n')
    assert not bilingual_corpus[-1, 1].endswith('\n')


def test_attributes_non_static():
    a = get_bilingual_corpus('Bulgarian', train_english=False)
    b = get_bilingual_corpus('Bulgarian', train_english=True)

    assert not a._train_english
    assert b._train_english


class TestDevoidOfUnicode:
    @pytest.mark.parametrize('language', [
        'Macedonian',
        'Persian',
        'Georgian',
        'Arabic',
        'Bulgarian',
        'Korean'
    ])
    def test_corpora_devoid_of_unicode_points(self, language):
        bilingual_corpus = get_bilingual_corpus(language)

        assert self._devoid_of_unicode_points(bilingual_corpus.english_corpus.character_set)
        assert self._devoid_of_unicode_points(bilingual_corpus.non_english_corpus.character_set)

    @staticmethod
    def _devoid_of_unicode_points(text: str) -> bool:
        return not re.findall(UNICODE_POINT_PATTERN, text)

    @pytest.mark.parametrize(
        'string, expected', [
            (r' !"%,-.0123456789:?ABCDEFGHIJKLMNOPRSTUVWYZabcdefghijklmnopqrstuvwxyz°ÄÖÜßáäöü’“„', True),
            (r' !"\',-.023:?ABCDEFGHIJKLMNOPRSTUVWYabcdefghijklmnopqrstuvwxyz₂', True),

            (r' !"\',-.023:?ABCDEFGHIJKLMNOPRSTUVWYabcdefghijklmnopqrstuvwxyz₂\xa2', False),
            (r' !"%\',-./0123456789:;?ABCDEFGHIJKLMNOPQRSTUVWYZabcdefghijklmnopqrstuvwxyz«°º»ÅÆÉØåæéíóöøüłŝŭǿ\u200b―₂', False),
            (r' !,.?ംഅആഇഈഉഊഎഏഐഒഓകഖഗഘങചഛജഞടഠഡണതഥദധനപഫബഭമയരറലളഴവശഷസഹാിീുൂൃെേൈൊോൌ്ൗൺൻർൽൾ\u200c\u200d', False)
        ]
    )
    def test__devoid_of_unicode_points(self, string, expected):
        assert self._devoid_of_unicode_points(string) == expected


@pytest.mark.parametrize('train_english', [
    True,
    False
])
def test_language_assignment(train_english):
    bilingual_corpus = get_bilingual_corpus('Bulgarian', train_english=train_english)

    assert len(asciiized(bilingual_corpus.english_corpus.character_set)) == pytest.approx(len(bilingual_corpus.english_corpus.character_set), abs=2)
    assert len(asciiized(bilingual_corpus.non_english_corpus.character_set)) != pytest.approx(len(bilingual_corpus.non_english_corpus.character_set), abs=2)


# ----------------
# Quote Stripping
# ----------------
@pytest.mark.parametrize('language, bilaterally_present_quotes', [
    # ('Italian', [
    #     '"Dang Me"',
    #     '"Chug-A-Lug"',
    #     '"Jingle Bells"',
    #     '''"You Don't Want My Love"''',
    #     '"In the Summer Time"',
    #     '"password"',
    #     '"Jailhouse Rock"'
    # ]),
    ('German', [
        '"Star Wars"',
        '"Tatoeba"',
        '"hipster"',
        '"Jingle Bells"'])
])
def test_bilaterally_present_quote_stripping(language, bilaterally_present_quotes):
    bilingual_corpus = BilingualCorpus(language)  # dont use 'get_bilingual_corpus' since data modification occurring
    bilingual_corpus.strip_bilaterally_present_quotes()

    assert not list(
        _bilaterally_present_strings(
            bilingual_corpus,
            query_strings=bilaterally_present_quotes,
            remove_special_characters=True
        )
    )


def _bilaterally_present_strings(
        sentence_data: BilingualCorpus,
        query_strings: List[str],
        remove_special_characters: bool) -> Iterator[str]:

    for sentence_pair in sentence_data:
        if remove_special_characters:
            sentence_pair = list(map(special_characters_stripped, sentence_pair))

        for query_string in query_strings:
            if query_string in sentence_pair[0] and query_string in sentence_pair[1]:
                query_strings.remove(query_string)
                yield query_string


# def find_sentences_comprising_string_bilaterally(sentence_data: BilingualCorpus, string: str) -> List[str]:
#     sentences = []
#
#     for english_sentence, foreign_language_sentence in sentence_data._sentence_pair_iterator:
#         if string in english_sentence and string in foreign_language_sentence:
#             sentences.append(' - '.join([english_sentence, foreign_language_sentence]))
#
#     return sentences


class TestCorpus:
    def test_ndarray_properties(self):
        corpus = get_bilingual_corpus('Macedonian', train_english=False).non_english_corpus

        assert corpus.shape == (62551,)
        assert corpus.dtype == np.dtype('<U136')
        assert isinstance(corpus[0], str)

    @pytest.mark.parametrize('language,expected', [
        ('French', True),
        ('Spanish', True),
        ('Croatian', True),
        ('Italian', True),
        ('Bosnian', True),

        ('Burmese', False),
        ('Korean', False),
        ('Bulgarian', False),
        ('Arabic', False),
        ('Serbian', False)
    ])
    def test_employs_latin_script(self, language, expected):
        assert get_bilingual_corpus(language).non_english_corpus.employs_latin_script == expected

    @pytest.mark.parametrize('language,tokens,expected', [
        ('German', ["c'est-à-dire"], False),
        ('French', ['Tom', 'Mary'], True),
        ('Italian', ['faccia', 'prigione', 'abbraccerà'], True),
        ('Korean', ['고마워', '잡아'], True)
    ])
    def test_comprises_tokens(self, language, tokens, expected):
        assert get_bilingual_corpus(language).non_english_corpus.comprises_tokens(query_tokens=tokens) == expected


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
#     assert list(map(sorted, BilingualCorpus(language).infer_forename_translations())) == expected
