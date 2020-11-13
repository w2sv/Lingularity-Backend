import os
import warnings
import zipfile

from backend.paths import SENTENCE_DATA_PATH, sentence_data_path
from backend.metadata import language_metadata
from backend.ops.data_mining import SENTENCE_DATA_PAGE_URL
from ._utils import patched_urllib

warnings.filterwarnings('ignore')


def download_sentence_data(language: str):
    """ Downloads and unzips respective sentence data file """

    print('Downloading sentence data...')
    zip_file_path = _download_sentence_data(language)
    _process_zip_file(zip_file_path, language)


def _download_sentence_data(language: str) -> str:
    """ Returns:
            absolute zip file save destination path """

    # assemble links
    zip_file_destination_path = f'{SENTENCE_DATA_PATH}/{language}.zip'
    download_link = f'{SENTENCE_DATA_PAGE_URL}/{language_metadata[language]["sentenceDataDownloadLinks"]["tatoebaProject"]}'

    # download zipfile
    patched_urllib._urlopener.retrieve(download_link, zip_file_destination_path)  # type: ignore

    return zip_file_destination_path


def _process_zip_file(zip_file_path: str, language: str):
    """ - unpack zip file
        - remove _about.txt
        - strip reference appendices from sentence data file
        - rename sentence data file """

    language_dir_path = zip_file_path[:zip_file_path.rfind(os.sep)]

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(language_dir_path)

    # remove unpacked zip file, about.txt
    os.remove(zip_file_path)
    os.remove(f'{language_dir_path}/_about.txt')

    _remove_reference_appendices((sentence_data_file_path := f'{language_dir_path}/{os.listdir(language_dir_path)[0]}'))

    # rename sentence data file
    os.rename(sentence_data_file_path, f'{sentence_data_path(language)}.txt')


def _remove_reference_appendices(sentence_data_file_path: str):
    raw_sentence_data = open(sentence_data_file_path, 'r', encoding='utf-8').readlines()
    processed_sentence_data = ('\t'.join(row.split('\t')[:2]) + '\n' for row in raw_sentence_data)

    with open(sentence_data_file_path, 'w', encoding='utf-8') as sentence_data_file:
        sentence_data_file.writelines(processed_sentence_data)
