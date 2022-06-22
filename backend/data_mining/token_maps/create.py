import os
from typing import Tuple

from tqdm import tqdm

from backend.metadata import language_metadata
from backend.paths import TOKEN_MAPS_PATH
from backend.trainers.components.mappings.token.occurrences import (create_token_occurrences_map, TokenOccurrencesMap)
from backend.trainers.components.mappings.token.sentence_indices import (
    get_token_sentence_indices_map,
    LemmaSentenceIndicesMap,
    SegmentSentenceIndicesMap
)
from backend.trainers.components.sentence_data import SentenceData
from backend.utils import io, string_resources
from .foundations import token_maps_foundations


def create_token_maps(language: str) -> Tuple[SegmentSentenceIndicesMap, TokenOccurrencesMap]:
    sentence_data = SentenceData(language=language)

    token_sentence_indices_map = get_token_sentence_indices_map(language=language, create=True)

    # procure token maps foundations
    sentence_indices_map_foundation, occurrence_map_foundations = token_maps_foundations(
        sentence_data=sentence_data,
        tokenize_with_pos_tags=token_sentence_indices_map.tokenize_with_pos_tags
    )

    # create token maps
    token_sentence_indices_map.create(sentence_index_2_unique_tokens=sentence_indices_map_foundation)
    token_occurrences_map = create_token_occurrences_map(
        paraphrases_tokens_list=occurrence_map_foundations[0],
        paraphrases_pos_tags_list=[None, occurrence_map_foundations[1]][
            type(token_sentence_indices_map) is LemmaSentenceIndicesMap]
    )

    return token_sentence_indices_map, token_occurrences_map


if __name__ == '__main__':
    for language in (progress_bar := tqdm(language_metadata.keys(), total=len(language_metadata))):
        if language not in os.listdir(TOKEN_MAPS_PATH) and language != string_resources.ENGLISH:
            progress_bar.set_description(f'Creating {language} maps...', refresh=True)

            # create maps
            token_sentence_indices_map, token_occurrences_map = create_token_maps(language=language)

            # create language-specific subdir
            language_dir = f'{TOKEN_MAPS_PATH}/{language}'
            os.mkdir(language_dir)

            # save maps
            io.write_pickle(token_sentence_indices_map.data, file_path=f'{language_dir}/sentence-indices-map')
            io.write_pickle(token_occurrences_map.data, file_path=f'{language_dir}/occurrences-map')
