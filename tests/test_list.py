import pytest
from subtypes.list import List_


@pytest.fixture
def default_list():
    return List_([0, 1, 1, 1, 2, 3, 4, 4, 5])


class TestList_:
    def test__slice_helper(self):
        assert True

    def test_after(self, default_list):
        assert default_list.after(3) == [4, 4, 5]
        with pytest.raises(ValueError):
            default_list.after(1)

    def test_after_first(self, default_list):
        assert default_list.after_first(4) == [4, 5]

    def test_after_last(self, default_list):
        assert default_list.after_last(4) == [5]

    def test_align_nested(self):
        assert True

    def test_append(self, default_list):
        ret = default_list.append(6)
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 3, 4, 4, 5, 6]

    def test_before(self, default_list):
        assert default_list.before(2) == [0, 1, 1, 1]
        with pytest.raises(ValueError):
            default_list.before(4)

    def test_before_first(self, default_list):
        assert default_list.before_first(1) == [0]

    def test_before_last(self, default_list):
        assert default_list.before_last(1) == [0, 1, 1]

    def test_clear(self, default_list):
        ret = default_list.clear()
        assert ret is default_list and not default_list

    def test_extend(self, default_list):
        ret = default_list.extend([6, 7])
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 3, 4, 4, 5, 6, 7]

    def test_flatten(self):
        assert List_([[1, 2], [3], [4, [5, 6]]]).flatten() == [1, 2, 3, 4, 5, 6]

    def test_from_(self, default_list):
        assert default_list.from_(3) == [3, 4, 4, 5]
        with pytest.raises(ValueError):
            default_list.from_(1)

    def test_from_first(self, default_list):
        assert default_list.from_first(4) == [4, 4, 5]

    def test_from_last(self, default_list):
        assert default_list.from_last(4) == [4, 5]

    def test_fuzzy_match_lists(self, default_list):
        assert True

    def test_insert(self, default_list):
        ret = default_list.insert(4, 2)
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 2, 3, 4, 4, 5]

    def test_remove(self, default_list):
        ret = default_list.remove(1)
        assert ret is default_list and default_list == [0, 1, 1, 2, 3, 4, 4, 5]

    def test_reverse(self, default_list):
        ret = default_list.reverse()
        assert ret is default_list and default_list == [5, 4, 4, 3, 2, 1, 1, 1, 0]

    def test_sort(self):
        unsorted = List_([3, 2, 5, 4, 1])
        ret = unsorted.sort()
        assert ret is unsorted and unsorted == [1, 2, 3, 4, 5]

    def test_until(self, default_list):
        assert default_list.until(3) == [0, 1, 1, 1, 2, 3]
        with pytest.raises(ValueError):
            default_list.until(1)

    def test_until_first(self, default_list):
        assert default_list.until_first(1) == [0, 1]

    def test_until_last(self, default_list):
        assert default_list.until_last(1) == [0, 1, 1, 1]
