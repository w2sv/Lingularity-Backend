""" https://spacy.io/usage/models

    TODO: extend by newly added models and create respective token maps """


import os
import subprocess

import spacy


def model_name(language: str, model_size='sm') -> str:
    """ Args:
            language: one of LANGUAGE_2_MODEL_IDENTIFIERS keys
            model_size: sm | md | lg """

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


def download_models():
    for language in LANGUAGE_2_MODEL_IDENTIFIERS.keys():
        spacy.cli.download(model_name(language=language))
        # _install_os_dependencies_if_required(language)


def _install_os_dependencies_if_required(language: str):
    # TODO: check if still required

    relative_os_dependency_installation_file_path = f'os-dependencies/languages/{language}.sh'

    if os.path.exists(f'{os.getcwd()}/{relative_os_dependency_installation_file_path}'):
        subprocess.run(f'bash {relative_os_dependency_installation_file_path}', shell=True)
