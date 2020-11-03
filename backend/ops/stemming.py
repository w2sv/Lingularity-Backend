from nltk.stem import SnowballStemmer


STEMMABLE_LANGUAGES = [language.title() for language in SnowballStemmer.languages]
