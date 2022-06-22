import os
from typing import Dict, Optional
import warnings

from backend.data_mining.data_mining import SENTENCE_DATA_DOWNLOAD_PAGE_URL
import pyzipper
import requests

from backend.paths import SENTENCE_DATA_PATH, sentence_data_path


warnings.filterwarnings('ignore')


def download_sentence_data(language: str, download_url_suffix: str, force_redownload=False):
    """ Downloads and unzips respective sentence data file

        Args:
            language: titular, written out
            download_url_suffix: e.g. 'deu-eng.zip'
            force_redownload: download despite data already been retrieved """

    if force_redownload or not os.path.exists(sentence_data_path(language)):
        zip_file_path = _download_zip_file(language, download_url_suffix)
        _process_zip_file(
            zip_file_path,
            language,
            tatoeba_language_identifier=_tatoeba_language_identifier(download_url_suffix)
        )
    else:
        print(f'{language} sentence data already downloaded; skipping')


def _tatoeba_language_identifier(download_url_suffix: str) -> str:
    return download_url_suffix.split('-')[0]


def _zip_file_path(language: str) -> str:
    return f'{SENTENCE_DATA_PATH}/{language}.zip'


def _download_zip_file(language: str, download_link_suffix: Optional[str]) -> str:
    """ Returns:
            zip file path """

    zip_file_path = _zip_file_path(language)

    _download_url(
        url=f'{SENTENCE_DATA_DOWNLOAD_PAGE_URL}{download_link_suffix}',
        save_path=zip_file_path,
        headers={
            'User-Agent':
                'Mozilla/5.0 (Windows NT 6.3; WOW64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/47.0.2526.69 Safari/537.36'
        }
    )
    return zip_file_path


def _download_url(url: str, save_path: str, headers: Dict, chunk_size=128):
    with requests.get(url, stream=True, headers=headers) as r:
        with open(save_path, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)


def _process_zip_file(zip_file_path: str, language: str, tatoeba_language_identifier: str):
    """ - unpack zip file
        - remove _about.txt, zip file
        - strip reference appendices from sentence data file
        - rename sentence data file """

    try:
        # unpack zip file
        with pyzipper.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(path=SENTENCE_DATA_PATH)

        # remove unpacked zip file, about.txt
        os.remove(zip_file_path)
        os.remove(f'{SENTENCE_DATA_PATH}/_about.txt')

        default_data_file_path = sentence_data_path(tatoeba_language_identifier)
        _remove_reference_appendices(default_data_file_path)

        # rename sentence data file
        os.rename(default_data_file_path, sentence_data_path(language))
    except pyzipper.BadZipFile:
        print(f"Couldn't extract {language} zipfile")


def _remove_reference_appendices(sentence_data_file_path: str):
    raw_sentence_data = open(sentence_data_file_path, 'r', encoding='utf-8').readlines()
    processed_sentence_data = ('\t'.join(row.split('\t')[:2]) + '\n' for row in raw_sentence_data)

    with open(sentence_data_file_path, 'w', encoding='utf-8') as sentence_data_file:
        sentence_data_file.writelines(processed_sentence_data)


if __name__ == '__main__':
    from backend.data_mining.online_data.scraping import sentence_data_download_links
    from tqdm import tqdm

    language_2_download_link_suffix = sentence_data_download_links.scrape()

    for language, download_link_suffix in (progress_bar := tqdm(
            language_2_download_link_suffix.items(),
            total=len(language_2_download_link_suffix)
    )):
        progress_bar.set_description(f'Downloading {language} sentence data', refresh=True)
        download_sentence_data(language, download_url_suffix=download_link_suffix, force_redownload=False)
