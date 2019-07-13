# import pytest
import datetime
from subtypes.datetime import DateTime

example_datetime = DateTime(1994, 3, 24)


def test_DateTimeAccessor___init__():
    assert True


def test_DateTime___repr__():
    assert True


def test_DateTime_casual_date():
    assert example_datetime.casual_date(full_month=True, day_first=True, day_suffix=True) == "24th March 1994"
    assert example_datetime.casual_date(full_month=False, day_first=False, day_suffix=False) == "Mar 24 1994"


def test_DateTime_delta():
    assert example_datetime.delta(years=26, months=-2, days=-23) == DateTime(2020, 1, 1)


def test_DateTime_filetag_date():
    assert example_datetime.filetag_date() == "19940324"


def test_DateTime_from_date():
    assert example_datetime == DateTime.from_date(datetime.date(1994, 3, 24))


def test_DateTime_from_datetime():
    assert example_datetime == DateTime.from_datetime(datetime.datetime(1994, 3, 24))


def test_DateTime_isoformat_date():
    assert example_datetime.isoformat_date(dashes=True, reverse=False) == "1994-03-24"
    assert example_datetime.isoformat_date(dashes=False, reverse=True) == "24031994"


def test_DateTime_logformat():
    assert example_datetime.logformat() == "[1994-03-24 00:00:00:000000]"


def test_DateTime_today():
    assert datetime.date.today() == DateTime.today().to_date()


def test_Day___init__():
    assert True


def test_Hour___init__():
    assert True


def test_MicroSecond___init__():
    assert True


def test_Minute___init__():
    assert True


def test_Month___init__():
    assert True


def test_Second___init__():
    assert True


def test_TimeZone___init__():
    assert True


def test_WeekDay___init__():
    assert True


def test_Week___init__():
    assert True


def test_Year___init__():
    assert True
