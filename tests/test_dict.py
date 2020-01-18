import pytest
from subtypes.dict import Dict_


@pytest.fixture
def example_dict():
    return Dict_({"one": 1, "two": 2, "three": 3, 4: "four", 5: "five", "done": None})


def test_is_special_private():  # synced
    assert True


def test_is_valid_for_attribute_actions():  # synced
    assert True


class TestRegexAccessor:
    def test___call__(self):  # synced
        assert True

    def test_filter(self, example_dict):  # synced
        assert example_dict.re.filter(r"one") == {"one": 1, "done": None}

    def test_get_all(self, example_dict):  # synced
        assert example_dict.re.get_all(r"one") == [1, None]

    def test_get_one(self, example_dict):  # synced
        with pytest.raises(KeyError):
            example_dict.getone_re(r"one")

        assert example_dict.re.get_one(r"^tw") == 2


class TestDictSettings:
    pass


class TestBaseDict:
    def test_update(self, example_dict):  # synced
        updated = example_dict.update({"six": 6, "done": True})
        assert updated.get("six") == 6 and updated.get("done") == True and example_dict is updated

    def test_clear(self, example_dict):  # synced
        cleared = example_dict.clear()
        assert cleared == {} and example_dict is cleared

    def test_copy(self):  # synced
        assert True


class TestDict_:
    def test___getitem__(self):  # synced
        assert True

    def test___setitem__(self):  # synced
        assert True

    def test___delitem__(self):  # synced
        assert True

    def test___getattr__(self):  # synced
        assert True

    def test___setattr__(self):  # synced
        assert True

    def test___delattr__(self):  # synced
        assert True

    def test__factory_(self):  # synced
        assert True

    def test_re(self):  # synced
        assert True

    def test_to_json(self):  # synced
        assert True

    def test_from_json():  # synced
        assert True
