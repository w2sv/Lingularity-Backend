def model_name(language: str, model_size='sm') -> str:
    return f'{LANGUAGE_2_MODEL_IDENTIFIERS[language][0]}_core_{LANGUAGE_2_MODEL_IDENTIFIERS[language][1]}_{model_size}'


LANGUAGE_2_MODEL_IDENTIFIERS = {
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

AVAILABLE_LANGUAGES = set(LANGUAGE_2_MODEL_IDENTIFIERS.keys())