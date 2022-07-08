import re

import numpy as np
import pytest

from backend.src.types.bilingual_corpus import bilaterally_present_quote_stripped
from backend.src.utils.strings.transformation import asciiized, UNICODE_POINT_PATTERN
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
@pytest.mark.parametrize('sentence_pair, expected', [
    (
        ('I have seen "Star Wars" twice.', 'Ich habe "Star Wars" zweimal gesehen.'),
        ('I have seen twice.', 'Ich habe zweimal gesehen.'),
    )
])
def test_bilaterally_present_quote_stripped(sentence_pair, expected):
    assert bilaterally_present_quote_stripped(sentence_pair) == expected


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
        ('Danish', ["c'est-à-dire"], False),
        ('Hebrew', ['HUUUUPEN', 'glocken'], False),
        ('Basque', ['giltza', 'Giltza'], False),
        ('Basque', ['giltza'], True),
        ('Greek', ['Επίθεση', 'Τομ'], True),
        ('Georgian', ['შენ', 'დარეკე'], True),
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
