import random

import pytest

from backend.trainers.base import ForenameConvertor


SEED = 69


italian_forename_converter = ForenameConvertor("Italian", train_english=False)


@pytest.mark.parametrize('sentence_pair,expected_sentence_pair', [
    (
            ["Unfortunately, Toms handy was stuck in Marys flytrap.", "Purtroppo, Toms Handy è rimasto bloccato nella trappola per mosche di Marie."],
            ['Unfortunately, Leonardos handy was stuck in Giulias flytrap.', 'Purtroppo, Leonardos Handy è rimasto bloccato nella trappola per mosche di Giulia.']
    ),
    (
            ["Tomorrow, Tom will cut the olive tree.", "Domani Tomás taglierà l'ulivo."],
            ['Tomorrow, Leonardo will cut the olive tree.', "Domani Leonardo taglierà l'ulivo."]
    ),
    (
            ["Tom told Mary that John wanted to ask Alice for a razor.", "Tom disse a Mary che John voleva chiedere ad Alice un rasoio."],
            ['Leonardo told Aurora that Alessandro wanted to ask Giulia for a razor.', 'Leonardo disse a Aurora che Alessandro voleva chiedere ad Giulia un rasoio.']
    ),
    (
            ["Tom's purpose in college is to get a degree.", "Lo scopo di Tom all'università è laurearsi."],
            ["Leonardo's purpose in college is to get a degree.", "Lo scopo di Leonardo all'università è laurearsi."]
    )
])
def test_forenames_conversion_italian(sentence_pair, expected_sentence_pair):
    random.seed(SEED)
    for converted, expected in zip(italian_forename_converter(sentence_pair), expected_sentence_pair):
        assert converted == expected


chinese_forename_converter = ForenameConvertor("Chinese", train_english=False)


@pytest.mark.parametrize('sentence_pair,expected_sentence_pair', [
    (
            ["Ask Tom.", "去问汤姆"],
            ['Ask Chia-hao.', '去问家豪']
    ),
    (
            ["Mary came in.", "瑪麗進來了。"],
            ['Shu-fen came in.', '淑芬進來了。']
    ),
    (
            ["Tom hugged Mary.", "汤姆拥抱了玛丽"],
            ['Chia-hao hugged Shu-hui.', '家豪拥抱了淑惠']
    ),
    (
            ["Tom is ecstatic.", "汤姆兴奋不已。"],
            ['Chia-hao is ecstatic.', '家豪兴奋不已。']
    ),
    (
            ["Mary doesn't wear as much makeup as Alice.", "玛丽没有化爱丽丝那样浓的妆。"],
            ["Shu-fen doesn't wear as much makeup as Mei-ling.", '淑芬没有化美玲那样浓的妆。']
    ),
    (
            ["I don't believe Tom's version of the story.", "我不相信汤姆的说法。"],
            ["I don't believe Chia-hao's version of the story.", '我不相信家豪的说法。']
    )
])
def test_forenames_conversion_chinese(sentence_pair, expected_sentence_pair):
    random.seed(SEED)
    for converted, expected in zip(chinese_forename_converter(sentence_pair), expected_sentence_pair):
        assert converted == expected
