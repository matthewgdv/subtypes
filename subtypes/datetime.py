from __future__ import annotations

import datetime as dt
from typing import Any, Union

from dateutil.relativedelta import relativedelta
import parsedatetime

from .lazy import cached_property
from .enums import Enum


_calendar = parsedatetime.Calendar()


class MetaInfoMixin:
    class Enums:
        class WeekDay(Enum):
            """An Enum holding the days of the week."""
            MONDAY = MON = Enum.Alias()
            TUESDAY = TUE = Enum.Alias()
            WEDNESDAY = WED = Enum.Alias()
            THURSDAY = THU = Enum.Alias()
            FRIDAY = FRI = Enum.Alias()
            SATURDAY = SAT = Enum.Alias()
            SUNDAY = SUN = Enum.Alias()

        class Month(Enum):
            """An Enum holding the months of the year."""
            JANUARY = JAN = Enum.Alias()
            FEBRUARY = FEB = Enum.Alias()
            MARCH = MAR = Enum.Alias()
            APRIL = APR = Enum.Alias()
            MAY = Enum.Auto()
            JUNE = JUN = Enum.Alias()
            JULY = JUL = Enum.Alias()
            AUGUST = AUG = Enum.Alias()
            SEPTEMBER = SEP = Enum.Alias()
            OCTOBER = OCT = Enum.Alias()
            NOVEMBER = NOV = Enum.Alias()
            DECEMBER = DEC = Enum.Alias()

    class FormatCode:
        """An Enum containing all the formatcodes used by DateTime.strptime() and DateTime.strftime(), subdivided into further Enums."""

        class TIMEZONE:
            NAME = "%Z"

        class WEEKDAY:
            SHORT, FULL, NUM = "%a", "%A", "%w"

        class WEEK:
            OF_YEAR_STARTING_MONDAY, OF_YEAR_STARTING_SUNDAY = "%W", "%U"

        class YEAR:
            WITHOUT_CENTURY, WITH_CENTURY = "%y", "%Y"

        class MONTH:
            SHORT, FULL, NUM = "%b", "%B", "%m"

        class DAY:
            NUM, OF_YEAR = "%d", "%j"

        class HOUR:
            H24, H12, AM_PM = "%H", "%I", "%p"

        class MINUTE:
            NUM = "%M"

        class SECOND:
            NUM = "%S"

        class MICROSECOND:
            NUM = "%f"


class Time(dt.time, MetaInfoMixin):
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 tzinfo: dt.timezone = None, *, fold=0) -> None:
        pass

    @classmethod
    def from_string(cls, text: str) -> Time:
        """Attempt to parse a string of text into a DateTime."""
        val, code = _calendar.parse(text)
        _, _, _, hour, minute, second, *_ = val

        if not (2 & code):
            raise ValueError(f"Could not parse stringlike value '{text}' to type '{cls.__name__}'.")

        return cls(hour, minute, second)


class Date(dt.date, MetaInfoMixin):
    """
    A subclass of the stdlib datetime.date class with additional useful methods.
    All normal datetime attributes are shadowed by PascalCase attributes which have properties providing various string representations of that attribute.
    E.g. Date.today().WeekDay.full, or Date.today().Year.without_century
    """

    def __init__(self, year: int, month: int, day: int) -> None:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.to_isoformat())})"

    def shift(self, years: int = 0, months: int = 0, days: int = 0, weeks: int = 0) -> Date:
        """Add/subtract the given amount of time units (as keyword arguments) to this DateTime. E.g. DateTime.now().delta(days=-3, hours=15)"""
        return self.from_date(self + relativedelta(years=years, months=months, days=days, weeks=weeks))

    def to_stdlib(self) -> dt.date:
        """Create the equivalent datetime.date object from this Date."""
        return dt.date.fromordinal(self.toordinal())

    def to_ordinal(self) -> int:
        return self.toordinal()

    def to_isoformat(self) -> str:
        """Create an isoformat date string from this Date with several options."""
        return self.strftime(f"{self.FormatCode.YEAR.WITH_CENTURY}-{self.FormatCode.MONTH.NUM}-{self.FormatCode.DAY.NUM}")

    def to_format(self, format_string: str) -> str:
        """Create a date string from this Date using a format string."""
        return self.strftime(format_string)

    def to_filetag(self) -> str:
        """Create a string suitable to be used as a date (not datetime!) tag within a filename."""
        return self.strftime(f"{self.FormatCode.YEAR.WITH_CENTURY}{self.FormatCode.MONTH.NUM}{self.FormatCode.DAY.NUM}")

    def to_casual(self, full_month: bool = False, day_first: bool = True, day_suffix: bool = False) -> str:
        """Create a human-readable datetime string from this DateTime with several options."""
        day, month, year = self.Day.with_suffix if day_suffix else self.day, self.Month.full if full_month else self.Month.short, self.Year.with_century
        return " ".join([str(item) for item in ((day, month, year) if day_first else (month, day, year))])

    @classmethod
    def today(cls, **kwargs: Any) -> Date:
        """Create a Date from today at midnight."""
        return cls.from_date(dt.date.today())

    @classmethod
    def from_date(cls, date: dt.date) -> Date:
        """Create a Date from a datetime.date object."""
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_ordinal(cls, ordinal: int) -> Date:
        """Create a Date from a datetime.datetime object."""
        return cls.fromordinal(ordinal)

    @classmethod
    def from_isoformat(cls, date_string: str) -> Date:
        """Create a Date from a datetime.datetime object."""
        return cls.fromisoformat(date_string)

    @classmethod
    def from_format(cls, date_string: str, format_string: str) -> Date:
        """Create a Date from a string representing a date and a format spec."""
        return DateTime.strptime(date_string, format_string).to_date()

    @classmethod
    def from_string(cls, text: str) -> Date:
        """Attempt to parse a string of text into a Date."""
        val, code = _calendar.parse(text)
        year, month, day, *_ = val

        if not (1 & code):
            raise ValueError(f"Could not parse stringlike value '{text}' to type '{cls.__name__}'.")

        return cls(year, month, day)

    @classmethod
    def infer(cls, datelike: Union[dt.datetime, dt.date, int, str]) -> Date:
        """Create a Date from a valid python object. Raises TypeError if an unsupported type is passed. Raises ValueError if an invalid instance of a supported type (like 'str' or 'int') is passed."""
        if isinstance(datelike, dt.datetime):
            return cls(datelike.year, datelike.month, datelike.day)
        elif isinstance(datelike, cls):
            return datelike
        elif isinstance(datelike, dt.date):
            return cls.from_date(datelike)
        elif isinstance(datelike, int):
            return cls.from_ordinal(datelike)
        elif isinstance(datelike, str):
            try:
                return cls.from_isoformat(datelike)
            except ValueError:
                return cls.from_string(datelike)
        else:
            raise TypeError(f"Unsupported type '{type(datelike)}' for inference to type '{cls.__name__}'.")

    @cached_property
    def WeekDay(self) -> WeekDay:
        return WeekDay(self)

    @cached_property
    def Week(self) -> Week:
        return Week(self)

    @cached_property
    def Year(self) -> Year:
        return Year(self)

    @cached_property
    def Month(self) -> Month:
        return Month(self)

    @cached_property
    def Day(self) -> Day:
        return Day(self)


class DateTime(Date, dt.datetime):
    """
    A subclass of the stdlib datetime.datetime class with additional useful methods.
    All normal datetime attributes are shadowed by PascalCase attributes which have properties providing various string representations of that attribute.
    E.g. DateTime.now().WeekDay.full, or DateTime.now().Year.without_century
    """
    nanosecond = 0

    def __init__(self, year: int, month: int, day: int,
                 hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 tzinfo: dt.timezone = None, *, fold=0) -> None:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}({repr(self.to_isoformat())})"

    def shift(self, years: int = 0, months: int = 0, days: int = 0, weeks: int = 0,
              hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0) -> DateTime:
        """Add/subtract the given amount of time units (as keyword arguments) to this DateTime. E.g. DateTime.now().delta(days=-3, hours=15)"""
        return self.from_datetime((self + relativedelta(years=years, months=months, days=days, weeks=weeks,
                                                        hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)))

    def to_date(self) -> Date:
        """Create the equivalent datetime.date object from this DateTime."""
        return Date.fromordinal(self.toordinal())

    def to_stdlib(self) -> dt.datetime:
        """Create the equivalent datetime.datetime object from this DateTime."""
        return dt.datetime.fromisoformat(self.isoformat())

    def to_isoformat(self, time: bool = True, timezone: bool = False) -> str:
        code = self.FormatCode
        text = self.to_format(f"{code.YEAR.WITH_CENTURY}-{code.MONTH.NUM}-{code.DAY.NUM}")

        if time and (self.hour or self.minute or self.second):
            text = self.to_format(f"{text} {code.HOUR.H24}:{code.MINUTE.NUM}:{code.SECOND.NUM}")

        if timezone and self.tzinfo is not None:
            text = f"{text}{self.tzinfo}"

        return text

    def to_format(self, format_string: str) -> str:
        """Create a datetime string from this DateTime using a format string."""
        return self.strftime(format_string)

    def to_logformat(self, labels: bool = False) -> str:
        """Create a precise datetime string suitable to be used for logging."""
        code = self.FormatCode
        if labels:
            return self.strftime(f"[{code.YEAR.WITH_CENTURY}-{code.MONTH.NUM}-{code.DAY.NUM} {code.HOUR.H24}h {code.MINUTE.NUM}m {code.SECOND.NUM}s {code.MICROSECOND.NUM}ms]")
        else:
            return self.strftime(f"[{code.YEAR.WITH_CENTURY}-{code.MONTH.NUM}-{code.DAY.NUM} {code.HOUR.H24}:{code.MINUTE.NUM}:{code.SECOND.NUM}:{code.MICROSECOND.NUM}]")

    @classmethod
    def from_datetime(cls, datetime: dt.datetime) -> DateTime:
        """Create a DateTime from a datetime.datetime object."""
        return cls.from_isoformat(datetime.isoformat())

    @classmethod
    def from_format(cls, date_string: str, format_string: str) -> DateTime:
        """Create a Date from a string representing a datetime and a format spec."""
        return DateTime.strptime(date_string, format_string)

    @classmethod
    def from_string(cls, text: str) -> DateTime:
        """Attempt to parse a string of text into a DateTime."""
        val, code = _calendar.parse(text)
        year, month, day, hour, minute, second, *_ = val

        if not (1 & code):
            raise ValueError(f"Could not parse stringlike value '{text}' to type '{cls.__name__}'.")

        return cls(year, month, day, hour, minute, second)

    @classmethod
    def infer(cls, datelike: Union[dt.datetime, dt.date, int, str]) -> DateTime:
        """Create a DateTime from a valid python object. Raises TypeError if an unsupported type is passed. Raises ValueError if an invalid instance of a supported type (like 'str' or 'int') is passed."""
        if isinstance(datelike, cls):
            return datelike
        elif isinstance(datelike, dt.datetime):
            return cls.from_datetime(datelike)
        elif isinstance(datelike, dt.date):
            return cls.from_date(datelike)
        elif isinstance(datelike, int):
            return cls.from_ordinal(datelike)
        elif isinstance(datelike, str):
            try:
                return cls.from_isoformat(datelike)
            except ValueError:
                if (ret := cls.from_string(datelike)) is not None:
                    return ret
                else:
                    raise ValueError(f"Could not parse stringlike value '{datelike}' to type '{cls.__name__}'.")
        else:
            raise TypeError(f"Unsupported type '{type(datelike)}' for inference to type '{cls.__name__}'.")

    @cached_property
    def TimeZone(self) -> TimeZone:
        return TimeZone(self)

    @cached_property
    def Hour(self) -> Hour:
        return Hour(self)

    @cached_property
    def Minute(self) -> Minute:
        return Minute(self)

    @cached_property
    def Second(self) -> Second:
        return Second(self)

    @cached_property
    def MicroSecond(self) -> MicroSecond:
        return MicroSecond(self)


class DateAccessor:
    def __init__(self, date: Date) -> None:
        self._date = date


class TimeZone(DateAccessor):
    @property
    def name(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.TIMEZONE.NAME)


class WeekDay(DateAccessor):
    @property
    def short(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.SHORT)

    @property
    def full(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.FULL)

    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.NUM)


class Week(DateAccessor):
    @property
    def of_year_starting_monday(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEK.OF_YEAR_STARTING_MONDAY)

    @property
    def of_year_starting_sunday(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEK.OF_YEAR_STARTING_SUNDAY)


class Year(DateAccessor):
    @property
    def without_century(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.YEAR.WITHOUT_CENTURY)

    @property
    def with_century(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.YEAR.WITH_CENTURY)


class Month(DateAccessor):
    @property
    def short(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.SHORT)

    @property
    def full(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.FULL)

    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.NUM)


class Day(DateAccessor):
    _suffixes = {day: suffix for days, suffix in [([1, 21, 31], "st"), ([2, 22], "nd"), ([3, 23], "rd")] for day in days}

    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.DAY.NUM)

    @property
    def of_year(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.DAY.OF_YEAR)

    @property
    def suffix(self) -> str:
        return self._suffixes.get(self._date.day, 'th')

    @property
    def with_suffix(self) -> str:
        return f"{self._date.day}{self.suffix}"


class Hour(DateAccessor):
    @property
    def h24(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.HOUR.H24)

    @property
    def h12(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.HOUR.H12)

    @property
    def am_pm(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.HOUR.AM_PM)


class Minute(DateAccessor):
    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MINUTE.NUM)


class Second(DateAccessor):
    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.SECOND.NUM)


class MicroSecond(DateAccessor):
    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MICROSECOND.NUM)
