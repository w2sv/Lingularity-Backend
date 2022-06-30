import pytest

from backend.src.trainers.vocable_trainer.deviation_masks import deviation_masks


@pytest.mark.parametrize('response,ground_truth,response_mask,ground_truth_mask', [
    ('scopare', 'scoprare', [False, False, False, False, False, False, False], [False, False, False, False, True, False, False, False]),
    ('scoprare', 'scopare', [False, False, False, False, True, False, False, False], [False, False, False, False, False, False, False]),
    ('scoprare', 'scoprare', [False, False, False, False, False, False, False, False], [False, False, False, False, False, False, False, False]),
    ('coptare', 'scopare', [False, False, False, True, False, False, False], [True, False, False, False, False, False, False]),
    ('scoprar', 'scoprare', [False, False, False, False, False, False, False], [False, False, False, False, False, False, False, True]),
    ('scopr', 'scoprare', [False, False, False, False, False], [False, False, False, False, False, True, True, True]),
    ('scaprara', 'scoprare', [False, False, True, False, False, False, False, True], [False, False, True, False, False, False, False, True]),
    ('opare', 'scopare', [False, False, False, False, False], [True, True, False, False, False, False, False]),
    ('scossare', 'scorsare', [False, False, False, True, False, False, False, False], [False, False, False, True, False, False, False, False]),
    ('scossarae', 'scossare', [False, False, False, False, False, False, False, True, False], [False, False, False, False, False, False, False, False]),
    ('scossaray', 'scossare', [False, False, False, False, False, False, False, True, True], [False, False, False, False, False, False, False, True])
])
def test_deviation_masks(response, ground_truth, response_mask, ground_truth_mask):
    masks = list(map(list, deviation_masks(response=response, ground_truth=ground_truth)))
    assert masks[0] == response_mask
    assert masks[1] == ground_truth_mask
