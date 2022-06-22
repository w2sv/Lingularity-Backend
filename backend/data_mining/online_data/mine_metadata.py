# type: ignore

import collections
from functools import partial
from typing import Dict, List, Union

from textacy.similarity import levenshtein
from tqdm import tqdm

from backend.data_mining.online_data.downloading.sentence_data import download_sentence_data
from backend.data_mining.online_data.scraping import countries, demonym, forenames, sentence_data_download_links
from backend.metadata.types import CountryMetadata, LanguageMetadata
from backend.ops.google.translation import GoogleTranslator
from backend.paths import META_DATA_PATH
from backend.trainers.components import SentenceData
from backend.trainers.components.forename_conversion import DEFAULT_FORENAMES
from backend.utils import io, string_resources
import backend.utils.strings.modification


language_metadata: LanguageMetadata = collections.defaultdict(lambda: {})
country_metadata: CountryMetadata = {}

google_translator = GoogleTranslator()

def _mine_metadata():
    language_2_download_link = sentence_data_download_links.scrape()
    print(language_2_download_link)

    # add English data
    language_metadata[string_resources.ENGLISH] = io.load_json(f'{META_DATA_PATH}/correction/language')[
        string_resources.ENGLISH]
    for country in language_metadata[string_resources.ENGLISH]['countriesEmployedIn']:
        print(country)
        _mine_and_set_forenames(country)

    for language, download_link in (progress_bar := tqdm(language_2_download_link.items(), total=len(language_2_download_link))):
        progress_bar.set_description(f'Mining {language} metadata', refresh=True)

        language_sub_dict = language_metadata[language]

        # set sentence data download links
        language_sub_dict['sentenceDataDownloadLinks'] = collections.defaultdict(lambda: {})
        language_sub_dict['sentenceDataDownloadLinks']['tatoebaProject'] = download_link

        # set generic properties
        download_sentence_data(language, download_url_suffix=download_link)
        sentence_data = SentenceData(language)

        language_sub_dict['properties'] = {}
        language_sub_dict['properties']['usesLatinScript'] = sentence_data.foreign_language_sentences.uses_latin_script

        language_sub_dict['nSentences'] = len(sentence_data)

        _mine_and_set_forename_conversion_data(language)
        _mine_and_set_translations(language, sentence_data=sentence_data)


def _mine_and_set_forename_conversion_data(language: str):
    language_metadata[language]['countriesEmployedIn'] = []

    try:
        if (countries_language_employed_in := countries.scrape(language)) is not None:
            for country in countries_language_employed_in:
                language_metadata[language]['countriesEmployedIn'].append(country)
                _mine_and_set_forenames(country)

    except ConnectionError as e:
        print(f'Obtained {e} when trying to scrape countries {language} employed in')


def _mine_and_set_forenames(country: str):
    if country_metadata.get(country, 'nil') == 'nil':
        if (_forenames := forenames.scrape(country)) is not None:
            country_metadata[country] = {
                'maleForenames': _spelling_map(_forenames, gender_index=0),
                'femaleForenames': _spelling_map(_forenames, gender_index=1),
                'demonym': demonym.scrape(country)
            }
        else:
            country_metadata[country] = None


def _spelling_map(_forenames: List[List[List[str]]], gender_index: int):
    return {
        'latinSpelling': _forenames[gender_index][0],
        'nativeSpelling': _forenames[gender_index][1]
    }


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
        translation_sub_dict["constitutionQuery"] = list(map(lambda query: backend.utils.strings.modification.replace_multiple(query, strings=sorted(translation_sub_dict["defaultForenames"]["Tom"], key=len, reverse=True) + [DEFAULT_FORENAMES[0]], replacement=FORENAME_PLACEHOLDER), constitution_queries))
    elif lets_go_translation := sentence_data.query_translation("Let's go!"):
        translation_sub_dict["letsGo"] = lets_go_translation

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
    correction_data = io.load_json(f'{META_DATA_PATH}/correction/{file_name}')
    for meta_key, sub_dict in correction_data.items():
        for sub_key, value in sub_dict.items():
            if isinstance(value, collections.Mapping):
                metadata[meta_key][sub_key] = {**(metadata[meta_key][sub_key] or {}), **value}
            else:
                metadata[meta_key][sub_key] = value


def _sort_dict_by_key(dictionary):
    return {k: v for k, v in sorted(dictionary.items())}


if __name__ == '__main__':
    # language_metadata = data.load_json(file_path=f'{META_DATA_PATH}/language')
    # for language in language_metadata.keys():
    #     if language != string_resources.ENGLISH:
    #         language_metadata[language]['nSentences'] = len(SentenceData(language))
    #
    # data.write_json(language_metadata, file_path=f'{META_DATA_PATH}/language')

    _mine_metadata()

    # sort data for legibility
    country_metadata = _sort_dict_by_key(country_metadata)
    language_metadata = _sort_dict_by_key(language_metadata)

    # correct country data
    _correct_metadata(country_metadata, 'country')

    io.write_json(language_metadata, file_path=f'{META_DATA_PATH}/language')
    io.write_json(country_metadata, file_path=f'{META_DATA_PATH}/country')
