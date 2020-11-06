from typing import Iterator, List, Generator, Tuple
from itertools import zip_longest, islice, starmap, chain, repeat

from backend.utils import iterables


def deviation_masks(response: str, ground_truth: str) -> Iterator[Iterator[bool]]:
    zipped_deviation_masks = _find_deviations(response, ground_truth)
    return starmap(lambda mask, corresponding_string, start_offset: islice(mask, start_offset, len(corresponding_string) + start_offset), zip(iterables.unzip(zipped_deviation_masks), [response, ground_truth], [zipped_deviation_masks.return_value, 0]))


_ZippedCharMask = Tuple[bool, bool]


@iterables.return_value_capturing_generator
def _find_deviations(response: str, ground_truth: str, response_mask_start_offset=0) -> Generator[_ZippedCharMask, None, int]:
    """ Yields:
            ZippedCharMasks, one of which is a mask of 2 boolean values
            representing whether or not the ith chars of response and ground_truth comprise a deviation
            with ZippedCharMasks[i][0] corresponding to response[i] and ZippedCharMasks[i][1] to ground_truth[i]

            Note:
                the length of the yielded iterator equals max(len(response), len(ground_truth)),
                _ZippedCharMask elements corresponding to response/ground_truth indices having
                exceeded the length of their underlying string are filled with False

        Returns:
            response_mask_start_offset: int, index at which actual response mask starts;
                coming into play on responses missing a prefix of the ground_truth, e.g.
                _find_deviations(response='ossare', ground_truth='scossare')
                 -> response_mask_start_offset = 2 """

    comparators = [response, ground_truth]

    for i, chars_i in enumerate(zip_longest(response, ground_truth)):

        if iterables.contains_singular_unique_value(chars_i):
            # -----Chars at parity-------

            yield False, False

        else:
            # -----Chars at disparity-------

            if not all(chars_i):
                # -----Length of one of the strings has been exceeded-------

                zipped_char_mask: List[bool] = [False, False]

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

                yield from chain(repeat([False, True], times=offset), _find_deviations(response, ground_truth[response_mask_start_offset:], response_mask_start_offset=offset))
                return response_mask_start_offset

            elif not iterables.contains_singular_unique_value(map(len, comparators)) or not iterables.contains_singular_unique_value(map(lambda string: string[i+1:], comparators)) and all(len(comparator) >= i + 2 for comparator in comparators):
                def check_for_superfluous_char() -> Generator[_ZippedCharMask, None, bool]:
                    """ impiaccio <-> impiccio """

                    if response[i + 1] == ground_truth[i]:
                        yield from chain([(True, False)], _find_deviations(response[i + 1:], ground_truth[i:], response_mask_start_offset=-1))
                        return True
                    return False

                def check_for_missing_char() -> Generator[_ZippedCharMask, None, bool]:
                    """ impicco <-> impiccio """

                    if response[i] == ground_truth[i + 1]:
                        yield from chain([(False, True)], _find_deviations(response[i:], ground_truth[i + 1:], response_mask_start_offset=-1))
                        return True
                    return False

                checks = [check_for_superfluous_char, check_for_missing_char]
                if len(response) < len(ground_truth):
                    checks = list(reversed(checks))

                for check in checks:
                    if (yield from check()):
                        return response_mask_start_offset

            yield True, True
    return response_mask_start_offset


if __name__ == '__main__':
    # scossare scorsare

    response_mask, ground_truth_mask = deviation_masks(response='opare', ground_truth='scopare')
    print(response_mask)
    print(ground_truth_mask)
