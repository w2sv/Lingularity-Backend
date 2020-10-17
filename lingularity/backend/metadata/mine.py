# type: ignore

from typing import Dict, Any, Union, List
import json
import collections
from functools import partial
import os

from tqdm import tqdm
from textacy.similarity import levenshtein

from lingularity.backend.resources import strings as string_resources
from lingularity.backend.components.forename_conversion import DEFAULT_FORENAMES
from lingularity.backend.metadata.types import LanguageMetadata, CountryMetadata
from lingularity.backend.trainers.base import SentenceData
from lingularity.backend.ops.google.translation import google_translator
from lingularity.backend.utils.strings import replace_multiple
from lingularity.backend.ops.data_mining.scraping import (
    scrape_sentence_data_download_links,
    scrape_countries_language_employed_in,
    scrape_popular_forenames, scrape_demonym
)


METADATA_DIR_PATH = f'{os.getcwd()}/lingularity/backend/resources/metadata'


def _save_as_json(data: Dict[Any, Any], file_name: str):
    with open(f'{METADATA_DIR_PATH}/{file_name}.json', 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, ensure_ascii=False, indent=4)


def _load_json(file_name: str) -> Dict[Any, Any]:
    with open(f'{METADATA_DIR_PATH}/{file_name}.json', 'r', encoding='utf-8') as read_file:
        return json.load(read_file)


def _mine_metadata():
    language_2_download_link = scrape_sentence_data_download_links()

    for language, download_link in (progress_bar := tqdm(language_2_download_link.items(), total=len(language_2_download_link))):
        progress_bar.set_description(f'Mining {language} metadata', refresh=True)

        language_sub_dict = language_metadata[language]

        # set sentence data download links
        language_sub_dict['sentenceDataDownloadLinks'] = collections.defaultdict(lambda: {})
        language_sub_dict['sentenceDataDownloadLinks']['tatoebaProject'] = download_link

        # set generic properties
        sentence_data = SentenceData(language)

        language_sub_dict['properties'] = {}
        language_sub_dict['properties']['usesLatinScript'] = sentence_data.foreign_language_sentences.uses_latin_script

        _mine_and_set_forename_conversion_data(language)
        _mine_and_set_translations(language, sentence_data=sentence_data)


def _mine_and_set_forename_conversion_data(language: str):
    language_metadata[language]['countriesEmployedIn'] = []

    try:
        if (countries_language_employed_in := scrape_countries_language_employed_in(language)) is not None:
            for country in countries_language_employed_in:
                language_metadata[language]['countriesEmployedIn'].append(country)

                if country_metadata.get(country, 'nil') == 'nil':
                    if (forenames := scrape_popular_forenames(country)) is not None:
                        def get_spelling_map(gender_index: int):
                            return {'latinSpelling': forenames[gender_index][0],
                                    'nativeSpelling': forenames[gender_index][1]}

                        country_metadata[country] = {
                            'maleForenames': get_spelling_map(gender_index=0),
                            'femaleForenames': get_spelling_map(gender_index=1),
                            'demonym': scrape_demonym(country)
                        }

                    else:
                        country_metadata[country] = None

    except ConnectionError as e:
        print(f'Obtained {e} when trying to scrape countries {language} employed in')


def _mine_and_set_translations(language: str, sentence_data: SentenceData):
    FORENAME_PLACEHOLDER = '{}'

    translation_sub_dict = {}

    if google_translator.available_for(language):
        translate = partial(google_translator.translate, src=string_resources.ENGLISH, dest=language)

        # lets go
        translation_sub_dict["letsGo"] = translate("Let's go!")

        # default forenames
        translation_sub_dict["defaultForenames"] = _get_default_forename_translations(sentence_data, language)

        # constitution query
        constitution_queries = map(translate, [f"How are you {DEFAULT_FORENAMES[0]}?", f"What's up {DEFAULT_FORENAMES[0]}?"])
        translation_sub_dict["constitutionQuery"] = list(map(lambda query: replace_multiple(query, strings=sorted(translation_sub_dict["defaultForenames"]["Tom"], key=len, reverse=True) + [DEFAULT_FORENAMES[0]], replacement=FORENAME_PLACEHOLDER), constitution_queries))

    language_metadata[language]['translations'] = translation_sub_dict


def _get_default_forename_translations(sentence_data: SentenceData, language: str) -> Dict[str, List[str]]:
    MIN_FORENAME_TRANSLATION_TRANSLATION_FORENAME_LEVENSHTEIN_SCORE = 0.55

    forename_2_translations = {}
    for forename, translations in zip(DEFAULT_FORENAMES, sentence_data.deduce_forename_translations()):
        translations = set(filter(lambda translation: levenshtein(forename, google_translator.translate(translation, dest=string_resources.ENGLISH, src=language)) >= MIN_FORENAME_TRANSLATION_TRANSLATION_FORENAME_LEVENSHTEIN_SCORE, translations))
        translations.add(google_translator.translate(forename, dest=language, src=string_resources.ENGLISH))
        translations.add(forename)
        forename_2_translations[forename] = sorted(translations, key=len, reverse=True)

    return forename_2_translations


def _correct_metadata(metadata: Union[LanguageMetadata, CountryMetadata], file_name: str):
    correction_data = _load_json(f'correction/{file_name}')
    for meta_key, sub_dict in correction_data.items():
        for sub_key, value in sub_dict.items():
            if isinstance(value, collections.abc.Mapping):
                metadata[meta_key][sub_key] = {**(metadata[meta_key][sub_key] or {}), **value}
            else:
                metadata[meta_key][sub_key] = value


if __name__ == '__main__':
    os.environ['MINING'] = "1"

    language_metadata: LanguageMetadata = collections.defaultdict(lambda: {})
    country_metadata: CountryMetadata = {}

    _mine_metadata()

    # sort country metadata for legibility
    country_metadata = {k: v for k, v in sorted(country_metadata.items())}

    # correct country metadata
    _correct_metadata(country_metadata, 'country')

    _save_as_json(language_metadata, file_name='language')
    _save_as_json(country_metadata, file_name='country')