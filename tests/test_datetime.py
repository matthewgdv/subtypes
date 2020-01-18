import pytest
import datetime as dt

from subtypes.datetime import Date, DateTime


@pytest.fixture
def example_date():
    return Date(1994, 3, 24)


@pytest.fixture
def example_datetime():
    return DateTime(1994, 3, 24, 12, 30, 15)


class TestFormatCode:
    class TestTIMEZONE:
        pass

    class TestWEEKDAY:
        pass

    class TestWEEK:
        pass

    class TestYEAR:
        pass

    class TestMONTH:
        pass

    class TestDAY:
        pass

    class TestHOUR:
        pass

    class TestMINUTE:
        pass

    class TestSECOND:
        pass

    class TestMICROSECOND:
        pass


class TestWeekDayName:
    pass


class TestMonthName:
    pass


class TestDate:
    def test_to_stdlib(self):  # synced
        assert True

    def test_to_ordinal(self):  # synced
        assert True

    def test_to_isoformat(self):  # synced
        assert example_date.to_isoformat() == "1994-03-24"

    def test_to_format(self):  # synced
        assert True

    def test_to_filetag(self):  # synced
        assert example_date.to_filetag() == "19940324"

    def test_to_casual(self, example_date):  # synced
        assert example_date.to_casual(full_month=True, day_first=True, day_suffix=True) == "24th March 1994"
        assert example_date.to_casual(full_month=False, day_first=False, day_suffix=False) == "Mar 24 1994"

    def test_today(self):  # synced
        assert True

    def test_from_date(self, example_date):  # synced
        assert example_date == Date.from_date(dt.date(1994, 3, 24))

    def test_from_ordinal(self):  # synced
        assert True

    def test_from_isoformat(self):  # synced
        assert True

    def test_from_format(self):  # synced
        assert True

    def test_from_datelike(self):  # synced
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


class TestDateTime:
    def test_delta(self):  # synced
        assert example_datetime.delta(years=26, months=-2, days=-23, hours=-12, minutes=-30, seconds=-15) == DateTime(2020, 1, 1)

    def test_truncate_time(self):  # synced
        assert True

    def test_to_date(self):  # synced
        assert True

    def test_to_stdlib(self):  # synced
        assert True

    def test_to_isoformat(self, example_datetime):  # synced
        assert example_datetime.to_isoformat() == "1994-03-24 12:30:15"

    def test_to_format(self):  # synced
        assert True

    def test_to_logformat(self, example_datetime):  # synced
        assert example_datetime.to_logformat() == "[1994-03-24 00:00:00:000000]"

    def test_from_datetime(self, example_datetime):  # synced
        assert example_datetime == DateTime.from_datetime(dt.datetime(1994, 3, 24))

    def test_from_format(self, example_datetime):  # synced
        assert True

    def test_from_string(self, example_datetime):  # synced
        assert True

    def test_from_datelike(self, example_datetime):  # synced
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


class TestDateAccessor:
    pass


class TestTimeZone:
    def test_name(self):  # synced
        assert True


class TestWeekDay:
    def test_short(self):  # synced
        assert True

    def test_full(self):  # synced
        assert True

    def test_num(self):  # synced
        assert True


class TestWeek:
    def test_of_year_starting_monday(self):  # synced
        assert True

    def test_of_year_starting_sunday(self):  # synced
        assert True


class TestYear:
    def test_without_century(self):  # synced
        assert True

    def test_with_century(self):  # synced
        assert True


class TestMonth:
    def test_short(self):  # synced
        assert True

    def test_full(self):  # synced
        assert True

    def test_num(self):  # synced
        assert True


class TestDay:
    def test_num(self):  # synced
        assert True

    def test_of_year(self):  # synced
        assert True

    def test_suffix(self):  # synced
        assert True

    def test_with_suffix(self):  # synced
        assert True


class TestHour:
    def test_h24(self):  # synced
        assert True

    def test_h12(self):  # synced
        assert True

    def test_am_pm(self):  # synced
        assert True


class TestMinute:
    def test_num(self):  # synced
        assert True


class TestSecond:
    def test_num(self):  # synced
        assert True


class TestMicroSecond:
    def test_num(self):  # synced
        assert True
