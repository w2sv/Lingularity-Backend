from typing import Dict
import re

from ._utils import read_page_source
from backend.ops.data_mining import SENTENCE_DATA_PAGE_URL


def scrape() -> Dict[str, str]:
    soup = read_page_source(SENTENCE_DATA_PAGE_URL)

    ZIP_LINK_PATTERN = re.compile('[a-z]{3}-[a-z]{3}.zip')

    language_2_zip_link = {}
    for data_link_text in filter(lambda link: '.zip' in link, map(lambda tag: tag.text, soup.find_all('li'))):
        data_link_text = data_link_text.strip('\t')
        language = data_link_text[:data_link_text.find('-')-1].split(' (')[0]

        language_2_zip_link[language] = re.finditer(ZIP_LINK_PATTERN, data_link_text)[0]
    return language_2_zip_link
