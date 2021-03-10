import pytest

from subtypes import Date, DateTime





@pytest.fixture
def example_datetime():
    return DateTime(1994, 3, 24, 12, 30, 15)


class TestDateAccessor:
    pass


class TestTimeAccessor:
    pass


class TestWeekDayAccessor:
    def test_short(self):  # synced
        assert True

    def test_full(self):  # synced
        assert True

    def test_num(self):  # synced
        assert True


class TestWeekAccessor:
    def test_of_year_starting_monday(self):  # synced
        assert True

    def test_of_year_starting_sunday(self):  # synced
        assert True


class TestYearAccessor:
    def test_without_century(self):  # synced
        assert True

    def test_with_century(self):  # synced
        assert True


class TestMonthAccessor:
    def test_short(self):  # synced
        assert True

    def test_full(self):  # synced
        assert True

    def test_num(self):  # synced
        assert True


class TestDayAccessor:
    def test_num(self):  # synced
        assert True

    def test_of_year(self):  # synced
        assert True

    def test_suffix(self):  # synced
        assert True

    def test_with_suffix(self):  # synced
        assert True


class TestTimeZoneAccessor:
    def test_name(self):  # synced
        assert True


class TestHourAccessor:
    def test_h24(self):  # synced
        assert True

    def test_h12(self):  # synced
        assert True

    def test_am_pm(self):  # synced
        assert True


class TestMinuteAccessor:
    def test_num(self):  # synced
        assert True


class TestSecondAccessor:
    def test_num(self):  # synced
        assert True


class TestMicroSecondAccessor:
    def test_num(self):  # synced
        assert True
