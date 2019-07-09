import pytest
from subtypes.dict import Dict_


@pytest.fixture
def example_dict():
    return Dict_({"one": 1, "two": 2, "three": 3, 4: "four", 5: "five", "done": None})


def test_dict_update(example_dict):
    updated = example_dict.update({"six": 6, "done": True})
    assert updated.get("six") == 6 and updated.get("done") == True and example_dict is updated


def test_dict_clear(example_dict):
    cleared = example_dict.clear()
    assert cleared == {} and example_dict is cleared


def test_dict_filter_re(example_dict):
    assert example_dict.filter_re(r"one") == {"one": 1, "done": None}


def test_dict_get_re(example_dict):
    assert example_dict.get_re(r"one") == [1, None]


def test_dict_getone_re(example_dict):
    with pytest.raises(KeyError):
        assert example_dict.getone_re(r"one")

    assert example_dict.getone_re(r"^tw") == 2
