from nltk.stem import SnowballStemmer


AVAILABLE_LANGUAGES = set(map(lambda language: language.title(), SnowballStemmer.languages))
