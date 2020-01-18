import pytest
from subtypes.list import List_


@pytest.fixture
def default_list():
    return List_([0, 1, 1, 1, 2, 3, 4, 4, 5])


class TestSliceAccessor:
    class TestSettings:
        pass

    def test___call__(self):  # synced
        assert True

    def test_before(self, default_list):  # synced
        assert default_list.slice.before(2) == [0, 1, 1, 1]
        with pytest.raises(ValueError):
            default_list.slice.before(4)

    def test_before_first(self, default_list):  # synced
        assert default_list.slice.before_first(1) == [0]

    def test_before_last(self, default_list):  # synced
        assert default_list.slice.before_last(1) == [0, 1, 1]

    def test_after(self, default_list):  # synced
        assert default_list.slice.after(3) == [4, 4, 5]
        with pytest.raises(ValueError):
            default_list.slice.after(1)

    def test_after_first(self, default_list):  # synced
        assert default_list.slice.after_first(4) == [4, 5]

    def test_after_last(self, default_list):  # synced
        assert default_list.slice.after_last(4) == [5]

    def test_from_(self, default_list):  # synced
        assert default_list.slice.from_(3) == [3, 4, 4, 5]
        with pytest.raises(ValueError):
            default_list.slice.from_(1)

    def test_from_first(self, default_list):  # synced
        assert default_list.slice.from_first(4) == [4, 4, 5]

    def test_from_last(self, default_list):  # synced
        assert default_list.slice.from_last(4) == [4, 5]

    def test_until(self, default_list):  # synced
        assert default_list.slice.until(3) == [0, 1, 1, 1, 2, 3]
        with pytest.raises(ValueError):
            default_list.slice.until(1)

    def test_until_first(self, default_list):  # synced
        assert default_list.slice.until_first(1) == [0, 1]

    def test_until_last(self, default_list):  # synced
        assert default_list.slice.until_last(1) == [0, 1, 1, 1]

    def test__slice_helper(self):  # synced
        assert True


class TestAttributeAccessor:
    def test___getattr__(self):  # synced
        assert True


class TestListSettings:
    pass


class TestBaseList:
    def test___add__(self):  # synced
        assert True

    def test___radd__(self):  # synced
        assert True

    def test___iadd__(self):  # synced
        assert True

    def test___mul__(self):  # synced
        assert True

    def test___rmul__(self):  # synced
        assert True

    def test___imul__(self):  # synced
        assert True

    def test_append(self):  # synced
        ret = default_list.append(6)
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 3, 4, 4, 5, 6]

    def test_extend(self):  # synced
        ret = default_list.extend([6, 7])
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 3, 4, 4, 5, 6, 7]

    def test_insert(self):  # synced
        ret = default_list.insert(4, 2)
        assert ret is default_list and default_list == [0, 1, 1, 1, 2, 2, 3, 4, 4, 5]

    def test_remove(self):  # synced
        ret = default_list.remove(1)
        assert ret is default_list and default_list == [0, 1, 1, 2, 3, 4, 4, 5]

    def test_reverse(self):  # synced
        ret = default_list.reverse()
        assert ret is default_list and default_list == [5, 4, 4, 3, 2, 1, 1, 1, 0]

    def test_sort(self):  # synced
        unsorted = List_([3, 2, 5, 4, 1])
        ret = unsorted.sort()
        assert ret is unsorted and unsorted == [1, 2, 3, 4, 5]

    def test_clear(self):  # synced
        ret = default_list.clear()
        assert ret is default_list and not default_list

    def test_copy(self):  # synced
        assert True


class TestList_:
    def test_slice(self):  # synced
        assert True

    def test_attr(self):  # synced
        assert True

    def test_apply(self):  # synced
        assert True

    def test_one(self):  # synced
        assert True

    def test_one_or_none(self):  # synced
        assert True

    def test_split_into_batches(self):  # synced
        assert True

    def test_split_into_batches_of_size(self):  # synced
        assert True

    def test_to_json(self):  # synced
        assert True

    def test_flatten(self):  # synced
        assert List_([[1, 2], [3], [4, [5, 6]]]).flatten() == [1, 2, 3, 4, 5, 6]

    def test__flatten_more(self):  # synced
        assert True

    def test_from_json(self):  # synced
        assert True
