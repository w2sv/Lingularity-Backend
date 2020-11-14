from typing import Optional
import os
import warnings
import zipfile
import requests
import shutil

from backend.paths import SENTENCE_DATA_PATH, sentence_data_path
from backend.ops.data_mining import SENTENCE_DATA_PAGE_URL


warnings.filterwarnings('ignore')


def download_sentence_data(language: str, download_link_suffix: str):
    """ Downloads and unzips respective sentence data file

        Args:
            language: titular, written out
            download_link_suffix: e.g. 'deu-eng.zip' """

    print(f'Downloading {language} sentence data...')
    _download_zip_file(language, download_link_suffix)
    _process_zip_file(language, tatoeba_language_identifier=download_link_suffix.split('-')[0])


def _zip_file_destination_path(language: str) -> str:
    return f'{SENTENCE_DATA_PATH}/{language}.zip'


def _download_zip_file(language: str, download_link_suffix: Optional[str]):
    HEADERS = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.3; WOW64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/47.0.2526.69 Safari/537.36'
    }

    with requests.get(url=f'{SENTENCE_DATA_PAGE_URL}/{download_link_suffix}', headers=HEADERS) as r:
        with open(_zip_file_destination_path(language), 'wb') as f:
            shutil.copyfileobj(r.raw, f)


def _process_zip_file(language: str, tatoeba_language_identifier: str):
    """ - unpack zip file
        - remove _about.txt, zip file
        - strip reference appendices from sentence data file
        - rename sentence data file """

    # unpack zip file
    with zipfile.ZipFile(_zip_file_destination_path(language), 'r') as zip_ref:
        zip_ref.extractall(path=SENTENCE_DATA_PATH)

    # remove unpacked zip file, about.txt
    os.remove(_zip_file_destination_path(language))
    os.remove(f'{SENTENCE_DATA_PATH}/_about.txt')

    default_data_file_path = sentence_data_path(tatoeba_language_identifier)
    _remove_reference_appendices(default_data_file_path)

    # rename sentence data file
    os.rename(default_data_file_path, sentence_data_path(language))


def _remove_reference_appendices(sentence_data_file_path: str):
    raw_sentence_data = open(sentence_data_file_path, 'r', encoding='utf-8').readlines()
    processed_sentence_data = ('\t'.join(row.split('\t')[:2]) + '\n' for row in raw_sentence_data)

    with open(sentence_data_file_path, 'w', encoding='utf-8') as sentence_data_file:
        sentence_data_file.writelines(processed_sentence_data)


if __name__ == '__main__':
    from backend.ops.data_mining.scraping import sentence_data_download_links

    for language, download_link_suffix in sentence_data_download_links.scrape().items():
        download_sentence_data(language, download_link_suffix=download_link_suffix)
