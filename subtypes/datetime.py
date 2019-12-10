from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Union

from django.utils.functional import cached_property as lazy_property
from dateutil.relativedelta import relativedelta
import parsedatetime

from .enums import Enum, ValueEnum


class FormatCode(ValueEnum):
    """An Enum containing all the formatcodes used by DateTime.strptime() and DateTime.strftime(), subdivided into further Enums."""
    class TIMEZONE(ValueEnum):
        NAME = "%Z"

    class WEEKDAY(ValueEnum):
        SHORT, FULL, NUM = "%a", "%A", "%w"

    class WEEK(ValueEnum):
        OF_YEAR_STARTING_MONDAY, OF_YEAR_STARTING_SUNDAY = "%W", "%U"

    class YEAR(ValueEnum):
        WITHOUT_CENTURY, WITH_CENTURY = "%y", "%Y"

    class MONTH(ValueEnum):
        SHORT, FULL, NUM = "%b", "%B", "%m"

    class DAY(ValueEnum):
        NUM, OF_YEAR = "%d", "%j"

    class HOUR(ValueEnum):
        H24, H12, AM_PM = "%H", "%I", "%p"

    class MINUTE(ValueEnum):
        NUM = "%M"

    class SECOND(ValueEnum):
        NUM = "%S"

    class MICROSECOND(ValueEnum):
        NUM = "%f"


class WeekDays(Enum):
    """An Enum holding the days of the week."""
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"


class DateTime(dt.datetime):
    """
    A subclass of the stdlib datetime.datetime class with additional useful methods.
    All normal datetime attributes are shadowed by PascalCase attributes which have properties providing various string representations of that attribute.
    E.g. DateTime.now().WeekDay.full, or DateTime.now().Year.without_century
    """
    nanosecond, FormatCode, WeekDays, calendar = 0, FormatCode, WeekDays, parsedatetime.Calendar()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([str(getattr(self, attr)) for attr in ['year', 'month', 'day', 'hour', 'minute', 'second'] if getattr(self, attr)])})"

    def delta(self, *args: Any, **kwargs: Any) -> DateTime:
        """Add/subtract the given amount of time units (as keyword arguments) to this DateTime. E.g. DateTime.now().delta(days=-3, hours=15)"""
        return self.fromisoformat((self + relativedelta(*args, **kwargs)).isoformat())

    def truncate_time(self) -> DateTime:
        return type(self)(self.year, self.month, self.day)

    def to_date(self) -> dt.date:
        """Create the equivalent datetime.date object from this DateTime."""
        return dt.date.fromordinal(self.toordinal())

    def to_datetime(self) -> dt.datetime:
        """Create the equivalent datetime.datetime object from this DateTime."""
        return dt.datetime.fromisoformat(self.isoformat())

    def to_ordinal(self) -> int:
        return self.toordinal()

    def to_isoformat(self, sep: str = " ", timespec: str = "seconds", show_tzinfo: bool = False) -> str:
        iso = self.isoformat(sep=sep, timespec=timespec)
        if show_tzinfo or self.tzinfo is None:
            return iso
        else:
            return str(Str(iso).slice.before(r"[+-]"))

    def to_isoformat_date(self) -> str:
        """Create an isoformat date string from this DateTime with several options."""
        return self.strftime(f"{FormatCode.YEAR.WITH_CENTURY}-{FormatCode.MONTH.NUM}-{FormatCode.DAY.NUM}")

    def to_casual_date(self, full_month: bool = False, day_first: bool = True, day_suffix: bool = False) -> str:
        """Create a human-readable datetime string from this DateTime with several options."""
        day, month, year = self.Day.with_suffix if day_suffix else self.day, self.Month.full if full_month else self.Month.short, self.Year.with_century
        return " ".join([str(item) for item in ((day, month, year) if day_first else (month, day, year))])

    def to_filetag(self) -> str:
        """Create a string suitable to be used as a date (not datetime!) tag within a filename."""
        return self.strftime(f"{FormatCode.YEAR.WITH_CENTURY}{FormatCode.MONTH.NUM}{FormatCode.DAY.NUM}")

    def to_logformat(self, labels: bool = False) -> str:
        """Create a precise datetime string suitable to be used for logging."""
        Code = FormatCode
        if labels:
            return self.strftime(f"[{Code.YEAR.WITH_CENTURY}-{Code.MONTH.NUM}-{Code.DAY.NUM} {Code.HOUR.H24}h {Code.MINUTE.NUM}m {Code.SECOND.NUM}s {Code.MICROSECOND.NUM}ms]")
        else:
            return self.strftime(f"[{Code.YEAR.WITH_CENTURY}-{Code.MONTH.NUM}-{Code.DAY.NUM} {Code.HOUR.H24}:{Code.MINUTE.NUM}:{Code.SECOND.NUM}:{Code.MICROSECOND.NUM}]")

    @classmethod
    def today(cls, **kwargs: Any) -> DateTime:
        """Create a DateTime from today at midnight."""
        return cls.from_date(dt.date.today())

    @classmethod
    def from_date(cls, date: dt.date) -> DateTime:
        """Create a DateTime from a datetime.date object."""
        return cls.fromordinal(date.toordinal())

    @classmethod
    def from_datetime(cls, datetime: dt.datetime) -> DateTime:
        """Create a DateTime from a datetime.datetime object."""
        return cls.fromisoformat(datetime.isoformat())

    @classmethod
    def from_string(cls, text: str) -> DateTime:
        """Attempt to parse a string of text into a DateTime. Returns None upon failure."""
        val, code = cls.calendar.parse(text)
        return cls(*val[:6 if code == 3 else 3]) if code in (1, 3) else None

    @classmethod
    def from_inference(cls, datelike: Union[dt.datetime, dt.date, int, str]) -> DateTime:
        """Create a DateTime from a valid python object. Raises TypeError if an unsupported type is passed. Raises ValueError if an invalid instance of a supported type (like 'str' or 'int') is passed."""
        if isinstance(datelike, cls):
            return datelike
        elif isinstance(datelike, dt.datetime):
            return cls.from_datetime(datelike)
        elif isinstance(datelike, dt.date):
            return cls.from_date(datelike)
        elif isinstance(datelike, int):
            return cls.fromordinal(datelike)
        elif isinstance(datelike, str):
            try:
                return cls.fromisoformat(datelike)
            except ValueError:
                if (ret := cls.from_string(datelike)) is not None:
                    return ret
                else:
                    raise ValueError(f"Could not parse stringlike value '{datelike}' to type '{cls.__name__}'.")
        else:
            raise TypeError(f"Unsupported type '{type(datelike)}' for inference to type '{cls.__name__}'.")

    @lazy_property
    def TimeZone(self) -> TimeZone:
        return TimeZone(self)

    @lazy_property
    def WeekDay(self) -> WeekDay:
        return WeekDay(self)

    @lazy_property
    def Week(self) -> Week:
        return Week(self)

    @lazy_property
    def Year(self) -> Year:
        return Year(self)

    @lazy_property
    def Month(self) -> Month:
        return Month(self)

    @lazy_property
    def Day(self) -> Day:
        return Day(self)

    @lazy_property
    def Hour(self) -> Hour:
        return Hour(self)

    @lazy_property
    def Minute(self) -> Minute:
        return Minute(self)

    @lazy_property
    def Second(self) -> Second:
        return Second(self)

    @lazy_property
    def MicroSecond(self) -> MicroSecond:
        return MicroSecond(self)


class DateTimeAccessor:
    def __init__(self, datetime: DateTime) -> None:
        self._datetime = datetime


class TimeZone(DateTimeAccessor):
    @property
    def name(self) -> str:
        return self._datetime.strftime(FormatCode.TIMEZONE.NAME)


class WeekDay(DateTimeAccessor):
    @property
    def short(self) -> str:
        return self._datetime.strftime(FormatCode.WEEKDAY.SHORT)

    @property
    def full(self) -> str:
        return self._datetime.strftime(FormatCode.WEEKDAY.FULL)

    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.WEEKDAY.NUM)


class Week(DateTimeAccessor):
    @property
    def of_year_starting_monday(self) -> str:
        return self._datetime.strftime(FormatCode.WEEK.OF_YEAR_STARTING_MONDAY)

    @property
    def of_year_starting_sunday(self) -> str:
        return self._datetime.strftime(FormatCode.WEEK.OF_YEAR_STARTING_SUNDAY)


class Year(DateTimeAccessor):
    @property
    def without_century(self) -> str:
        return self._datetime.strftime(FormatCode.YEAR.WITHOUT_CENTURY)

    @property
    def with_century(self) -> str:
        return self._datetime.strftime(FormatCode.YEAR.WITH_CENTURY)


class Month(DateTimeAccessor):
    @property
    def short(self) -> str:
        return self._datetime.strftime(FormatCode.MONTH.SHORT)

    @property
    def full(self) -> str:
        return self._datetime.strftime(FormatCode.MONTH.FULL)

    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.MONTH.NUM)


class Day(DateTimeAccessor):
    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.DAY.NUM)

    @property
    def of_year(self) -> str:
        return self._datetime.strftime(FormatCode.DAY.OF_YEAR)

    @property
    def suffix(self) -> str:
        return self._suffixes.get(self._datetime.day, 'th')

    @property
    def with_suffix(self) -> str:
        return f"{self._datetime.day}{self.suffix}"

    @lazy_property
    def _suffixes(self) -> Dict[int, str]:
        return {day: suffix for days, suffix in [([1, 21, 31], "st"), ([2, 22], "nd"), ([3, 23], "rd")] for day in days}


class Hour(DateTimeAccessor):
    @property
    def h24(self) -> str:
        return self._datetime.strftime(FormatCode.HOUR.H24)

    @property
    def h12(self) -> str:
        return self._datetime.strftime(FormatCode.HOUR.H12)

    @property
    def am_pm(self) -> str:
        return self._datetime.strftime(FormatCode.HOUR.AM_PM)


class Minute(DateTimeAccessor):
    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.MINUTE.NUM)


class Second(DateTimeAccessor):
    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.SECOND.NUM)


class MicroSecond(DateTimeAccessor):
    @property
    def num(self) -> str:
        return self._datetime.strftime(FormatCode.MICROSECOND.NUM)
