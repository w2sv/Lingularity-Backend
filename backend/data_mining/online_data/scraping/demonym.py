from itertools import islice
from typing import Optional

from bs4 import BeautifulSoup
from textacy.similarity import levenshtein

from ._utils import read_page_source


def scrape(country_name: str) -> Optional[str]:
    """
        Args:
            country_name: uppercase
        Returns:
            None in case of irretrievability, otherwise best fit country_demonym """

    page_url = f'http://en.wikipedia.org/wiki/{country_name}'

    soup: BeautifulSoup = read_page_source(page_url)

    if (demonym_tag := soup.find('a', href='/wiki/Demonym')) is None:
        return None

    def is_demonym(_demonym_candidate) -> bool:
        return country_name.startswith(_demonym_candidate[:2])

    demonym: Optional[str] = None
    for element in islice(demonym_tag.next_elements, 1, 10):
        if element.name is None:
            for demonym_candidate in filter(lambda c: c.istitle(), element.split(' ')):
                if demonym is None:
                    demonym = demonym_candidate
                else:
                    if is_demonym(demonym_candidate) and levenshtein(country_name, demonym_candidate) > levenshtein(country_name, demonym):
                        demonym = demonym_candidate

    return demonym
