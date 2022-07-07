from itertools import chain, islice, repeat, starmap, zip_longest
from typing import Generator, Iterator

from backend.src.utils import iterables
from backend.src.utils.return_value_capturing_generator import ReturnValueCapturingGenerator


_DeviationMask = Iterator[bool]


def deviation_masks(response: str, ground_truth: str) -> Iterator[_DeviationMask]:
    """ Yields:
            response deviation mask, ground truth deviation mask (to be interpreted as
            emphasis mask, indicating chars which have been missed) whose lengths are at
            parity with the one of their underlying string """

    zipped_deviation_mask = ReturnValueCapturingGenerator(_ith_char_mask_iterator(response, ground_truth))

    comparator_masks = zip(*zipped_deviation_mask)
    comparators = [response, ground_truth]
    start_offsets = [zipped_deviation_mask.value, 0]

    # unzip ith char masks, indent response by found start offset
    return starmap(
        lambda mask, comparator, start_offset: islice(
            mask,
            start_offset,
            len(comparator) + start_offset
        ),
        zip(
            comparator_masks,
            comparators,
            start_offsets
        )
    )


_IthCharMask = tuple[bool, bool]


def _ith_char_mask_iterator(response: str, ground_truth: str, response_mask_start_offset=0) -> Generator[_IthCharMask, None, int]:
    """ Yields:
            ZippedCharMasks, one of which is a mask of 2 boolean values
            representing whether the ith chars of response and ground_truth comprise a deviation
            with ZippedCharMasks[i][0] corresponding to response[i] and ZippedCharMasks[i][1] to ground_truth[i]

            Note:
                the length of the yielded iterator equals max(len(response), len(ground_truth)),
                _IthCharMask elements corresponding to response/ground_truth indices having
                exceeded the length of their underlying string are filled with False

        Returns:
            response_mask_start_offset: int, index at which actual response mask starts;
                coming into play on responses missing a prefix of the ground_truth, e.g.
                _ith_char_mask_iterator(response='ossare', ground_truth='scossare')
                 -> response_mask_start_offset = 2 """

    comparators = [response, ground_truth]

    for i, chars_i in enumerate(zip_longest(response, ground_truth)):

        if iterables.contains_unique_value(chars_i):
            # -----Chars at parity-------

            yield False, False

        else:
            # -----Chars at disparity-------

            if not all(chars_i):
                # -----Length of one of the strings has been exceeded-------

                zipped_char_mask = [False, False]

                # iterate over chars_i to determine exceeded string
                # and thus the zipped_char_mask for the remaining indices
                for j, char_ij in enumerate(chars_i):
                    if not char_ij and chars_i[not j]:
                        zipped_char_mask[not j] = True

                        # yield zipped_char_mask (len(max_len_string) - len(exceeded_string)) times
                        # and exit afterwards
                        for _ in range(i, len(comparators[not j])):
                            yield tuple(zipped_char_mask)  # type: ignore
                        return response_mask_start_offset

            elif not i and not response_mask_start_offset and (offset := ground_truth.find(response[:2])) != -1:
                # -----Response missing a prefix of the ground truth-------

                # yield len(missing_prefix) zipped_char_masks indicating response deviation
                # and recurse with indented ground_truth
                yield from chain(repeat([False, True], times=offset), _ith_char_mask_iterator(response, ground_truth[offset:], response_mask_start_offset=offset))
                return offset

            elif all(map(lambda comparator: iterables.comprises_index(comparator, i), comparators)) and (not iterables.length_parity(response, ground_truth) or response[i + 1:] != ground_truth[i + 1:]):
                # -----Char deviation possibly caused by substring shift-------

                def check_for_superfluous_char() -> Generator[_IthCharMask, None, bool]:
                    """ e.g. response=impiaccio, ground_truth=impiccio """

                    try:
                        if response[i + 1] == ground_truth[i]:
                            yield from chain([(True, False)], _ith_char_mask_iterator(response[i + 1:], ground_truth[i:], response_mask_start_offset=-1))
                            return True
                    except IndexError:
                        pass
                    return False

                def check_for_missing_char() -> Generator[_IthCharMask, None, bool]:
                    """ e.g. response=impicco, ground_truth=impiccio """

                    try:
                        if response[i] == ground_truth[i + 1]:
                            yield from chain([(False, True)], _ith_char_mask_iterator(response[i:], ground_truth[i + 1:], response_mask_start_offset=-1))
                            return True
                    except IndexError:
                        pass
                    return False

                # sort checks wrt comparator length discrepancy since
                # longer response -> higher probability of superfluous char
                checks = [check_for_superfluous_char, check_for_missing_char]
                if len(response) < len(ground_truth):
                    checks = list(reversed(checks))

                # recurse and return if either_or of the checks successful
                for check in checks:
                    if (yield from check()):
                        return response_mask_start_offset

            # -----Plain char deviation not caused by substring shift-------
            yield True, True

    return response_mask_start_offset
