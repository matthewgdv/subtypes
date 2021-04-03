import pytest
import datetime as dt

from subtypes import DateTime


@pytest.fixture
def example_datetime():
    return DateTime(1994, 3, 24, 12, 30, 15)


class TestDateTime:
    def test___str__(self):  # synced
        assert True

    def test_shift(self, example_datetime):  # synced
        assert example_datetime.shift(years=26, months=-2, days=-23, hours=-12, minutes=-30, seconds=-15) == DateTime(2020, 1, 1)

    def test_date(self):  # synced
        assert True

    def test_time(self):  # synced
        assert True

    def test_to_stdlib(self):  # synced
        assert True

    def test_to_isoformat(self, example_datetime):  # synced
        assert example_datetime.to_isoformat() == "1994-03-24 12:30:15"

    def test_to_format(self):  # synced
        assert True

    def test_from_datetime(self, example_datetime):  # synced
        assert example_datetime == DateTime.from_datetime(dt.datetime(1994, 3, 24, 12, 30, 15))

    def test_from_isoformat(self):  # synced
        assert True

    def test_from_format(self):  # synced
        assert True

    def test_from_string(self):  # synced
        assert True

    def test_from_parts(self):  # synced
        assert True

    def test_infer(self):  # synced
        assert True

    def test_TimeZone(self):  # synced
        assert True

    def test_Hour(self):  # synced
        assert True

    def test_Minute(self):  # synced
        assert True

    def test_Second(self):  # synced
        assert True

    def test_MicroSecond(self):  # synced
        assert True
