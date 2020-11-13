from typing import Optional
import os
import warnings
import zipfile

from backend.paths import SENTENCE_DATA_PATH, sentence_data_path
from backend.metadata import language_metadata
from backend.ops.data_mining import SENTENCE_DATA_PAGE_URL
from ._utils import patched_urllib

warnings.filterwarnings('ignore')


def download_sentence_data(language: str, zip_file_download_link: Optional[str] = None):
    """ Downloads and unzips respective sentence data file """

    print('Downloading sentence data...')
    language, tatoeba_language_identifier = _download_sentence_data(language, zip_file_download_link)
    _process_zip_file(language, tatoeba_language_identifier)


def _zip_file_destination_path(language: str) -> str:
    return f'{SENTENCE_DATA_PATH}/{language}.zip'


def _download_sentence_data(language: str, zip_file_download_link: Optional[str]) -> str:
    """ Returns:
            absolute zip file save destination path """

    if not zip_file_download_link:
        zip_file_download_link = [language_metadata[language]["sentenceDataDownloadLinks"]["tatoebaProject"]]

    # download zipfile
    patched_urllib._urlopener.retrieve(
        f'{SENTENCE_DATA_PAGE_URL}/{zip_file_download_link}',
        _zip_file_destination_path(language))  # type: ignore

    return language, zip_file_download_link.split('-')[0]


def _process_zip_file(language: str, identifier: str):
    """ - unpack zip file
        - remove _about.txt
        - strip reference appendices from sentence data file
        - rename sentence data file """

    # decompress zip file
    with zipfile.ZipFile(_zip_file_destination_path(language), 'r') as zip_ref:
        zip_ref.extractall(path=SENTENCE_DATA_PATH)

    # remove unpacked zip file, about.txt
    os.remove(_zip_file_destination_path(language))
    os.remove(f'{SENTENCE_DATA_PATH}/_about.txt')

    _remove_reference_appendices((default_data_file_path := sentence_data_path(identifier)))

    # rename sentence data file
    os.rename(default_data_file_path, sentence_data_path(language))


def _remove_reference_appendices(sentence_data_file_path: str):
    raw_sentence_data = open(sentence_data_file_path, 'r', encoding='utf-8').readlines()
    processed_sentence_data = ('\t'.join(row.split('\t')[:2]) + '\n' for row in raw_sentence_data)

    with open(sentence_data_file_path, 'w', encoding='utf-8') as sentence_data_file:
        sentence_data_file.writelines(processed_sentence_data)
