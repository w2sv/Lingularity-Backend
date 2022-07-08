""" https://spacy.io/models """


import spacy


def load_model(language: str) -> spacy.Language:
    print('Loading model...')
    return spacy.load(model_name(language=language))


def model_name(language: str, model_size='sm') -> str:
    """ Args:
            language: one of LANGUAGE_2_MODEL_PARAMETERS keys
            model_size: sm | md | lg """

    return f'{LANGUAGE_2_MODEL_PARAMETERS[language][0]}_core_{LANGUAGE_2_MODEL_PARAMETERS[language][1]}_{model_size}'


LANGUAGE_2_MODEL_PARAMETERS = {
    'Chinese': ['zh', 'web'],
    'Danish': ['da', 'news'],
    'Dutch': ['nl', 'news'],
    'English': ['en', 'web'],
    'French': ['fr', 'news'],
    'German': ['de', 'news'],
    'Greek': ['el', 'news'],
    'Italian': ['it', 'news'],
    'Japanese': ['ja', 'news'],
    'Lithuanian': ['lt', 'news'],
    'Norwegian': ['nb', 'news'],
    'Polish': ['pl', 'news'],
    'Portuguese': ['pt', 'news'],
    'Romanian': ['ro', 'news'],
    'Spanish': ['es', 'news']
}

AVAILABLE_LANGUAGES = set(LANGUAGE_2_MODEL_PARAMETERS.keys())