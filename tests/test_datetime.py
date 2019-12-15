# import pytest
import datetime
from subtypes.datetime import DateTime

example_datetime = DateTime(1994, 3, 24)


class TestDateTimeAccessor:
    def test___init__(self):
        assert True


class TestDateTime:
    def test___repr__(self):
        assert True

    def test_casual_date(self):
        assert example_datetime.to_casual_date(full_month=True, day_first=True, day_suffix=True) == "24th March 1994"
        assert example_datetime.to_casual_date(full_month=False, day_first=False, day_suffix=False) == "Mar 24 1994"

    def test_delta(self):
        assert example_datetime.delta(years=26, months=-2, days=-23) == DateTime(2020, 1, 1)

    def test_filetag(self):
        assert example_datetime.to_filetag() == "19940324"

    def test_from_date(self):
        assert example_datetime == DateTime.from_date(datetime.date(1994, 3, 24))

    def test_from_datetime(self):
        assert example_datetime == DateTime.from_datetime(datetime.datetime(1994, 3, 24))

    def test_isoformat_date(self):
        assert example_datetime.to_isoformat_date() == "1994-03-24"

    def test_logformat(self):
        assert example_datetime.to_logformat() == "[1994-03-24 00:00:00:000000]"

    def test_today(self):
        assert datetime.date.today() == DateTime.today().to_date()


class TestDay:
    def test___init__(self):
        assert True


class TestHour:
    def test___init__(self):
        assert True


class TestMicroSecond:
    def test___init__(self):
        assert True


class TestMinute:
    def test___init__(self):
        assert True


class TestMonth:
    def test___init__(self):
        assert True


class TestSecond:
    def test___init__(self):
        assert True


class TestTimeZone:
    def test___init__(self):
        assert True


class TestWeekDay:
    def test___init__(self):
        assert True


class TestWeek:
    def test___init__(self):
        assert True


class TestYear:
    def test___init__(self):
        assert True
