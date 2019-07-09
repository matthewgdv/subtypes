import datetime
import pytest
from subtypes.datetime import DateTime

example_datetime = DateTime(1994, 3, 24)


def test_datetime_today():
    assert datetime.date.today() == DateTime.today()


def test_datetime_now():
    assert True


def test_datetime_from_date():
    assert example_datetime == DateTime.from_date(datetime.date(2019, 3, 24))


def test_datetime_from_datetime():
    assert example_datetime == DateTime.from_datetime(datetime.datetime(2019, 3, 24))


def test_datetime_casual_date():
    assert example_datetime.casual_date(full_month=True, day_first=True, day_suffix=True) == "24th March 1994"
    assert example_datetime.casual_date(full_month=False, day_first=False, day_suffix=False) == "Mar 24 1994"


def test_datetime_isoformat_date():
    assert example_datetime.isoformat_date(dashes=True, reverse=False) == "1994-03-24"
    assert example_datetime.isoformat_date(dashes=False, reverse=True) == "24031994"


def test_datetime_filetag_date():
    assert example_datetime.filetag_date() == "19940324"


def test_datetime_logformat():
    assert example_datetime.logformat() == "[1994-03-24 00:00:00:000000]"


def test_datetime_delta():
    assert False
