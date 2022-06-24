from typing import Callable

from backend.components import Corpus
from . import diction_expansion, random, simple


SentenceDataFilter = Callable[[Corpus, str], Corpus]


if __name__ == '__main__':

    language = 'Italian'

    sentence_data = Corpus(language, train_english=False)
    print(f'# sentences: {len(sentence_data)}')

    filtered_sentence_data = simple.filter_sentence_data(sentence_data, language)

    print(f'# filtered sentences simple: {len(filtered_sentence_data)}')
    # print(filtered_sentence_data[-30:])
