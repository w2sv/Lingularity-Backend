from typing import List
import os
import subprocess

from backend.ops.normalizing.lemmatizing import _assemble_model_name, LANGUAGE_2_MODEL_IDENTIFIERS


def model_package_links(version: str) -> List[str]:
    def package_link(language):
        model_name = _assemble_model_name(language)
        return f"{model_name} @ https://github.com/explosion/spacy-models/releases/download/{model_name}-{version}/{model_name}-{version}.tar.gz"

    return [package_link(language) for language in LANGUAGE_2_MODEL_IDENTIFIERS.keys()]


ADDITIONAL_DEPENDENCIES = [
            'sudachipy sudachidict_core',
            'jieba'
        ]


if __name__ == '__main__':
    """ Download all available spacy models alongside additional dependencies """


    def download_models():
        for language in LANGUAGE_2_MODEL_IDENTIFIERS.keys():
            subprocess.run(f'python -m spacy download {_assemble_model_name(language=language)}', shell=True)
            _install_os_dependencies_if_required(language)


    def _install_os_dependencies_if_required(language: str):
        relative_os_dependency_installation_file_path = f'os-dependencies/languages/{language}.sh'

        if os.path.exists(f'{os.getcwd()}/{relative_os_dependency_installation_file_path}'):
            subprocess.run(f'bash {relative_os_dependency_installation_file_path}', shell=True)


    def install_additional_dependencies():
        for dependency in ADDITIONAL_DEPENDENCIES:
            subprocess.run(f'pip install {dependency}')

    download_models()
    install_additional_dependencies()
