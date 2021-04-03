import pytest
import datetime as dt

from subtypes import Date


@pytest.fixture
def example_date():
    return Date(1994, 3, 24)


class TestDate:
    def test___str__(self):  # synced
        assert True

    def test_shift(self):  # synced
        assert True

    def test_to_stdlib(self):  # synced
        assert True

    def test_to_ordinal(self):  # synced
        assert True

    def test_to_isoformat(self, example_date):  # synced
        assert example_date.to_isoformat() == "1994-03-24"

    def test_to_format(self):  # synced
        assert True

    def test_to_filetag(self, example_date):  # synced
        assert example_date.to_filetag() == "19940324"

    def test_to_casual(self, example_date):  # synced
        assert example_date.to_casual(full_month=True, day_first=True, day_suffix=True) == "24th March 1994"
        assert example_date.to_casual(full_month=False, day_first=False, day_suffix=False) == "Mar 24 1994"

    def test_today(self):  # synced
        assert True

    def test_from_date(self, example_date):  # synced
        assert example_date == dt.date(1994, 3, 24)

    def test_from_ordinal(self):  # synced
        assert True

    def test_from_isoformat(self):  # synced
        assert True

    def test_from_format(self):  # synced
        assert True

    def test_from_string(self):  # synced
        assert True

    def test_infer(self):  # synced
        assert True

    def test_WeekDay(self):  # synced
        assert True

    def test_Week(self):  # synced
        assert True

    def test_Year(self):  # synced
        assert True

    def test_Month(self):  # synced
        assert True

    def test_Day(self):  # synced
        assert True
