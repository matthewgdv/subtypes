from __future__ import annotations

import datetime as dt
from typing import Any, cast

from lazy_property import LazyProperty
from dateutil.relativedelta import relativedelta

from .enum import Enum


class FormatCode(Enum):
    class TIMEZONE(Enum):
        NAME = "%Z"

    class WEEKDAY(Enum):
        SHORT, FULL, NUM = "%a", "%A", "%w"

    class WEEK(Enum):
        OF_YEAR_STARTING_MONDAY, OF_YEAR_STARTING_SUNDAY = "%W", "%U"

    class YEAR(Enum):
        WITHOUT_CENTURY, WITH_CENTURY = "%y", "%Y"

    class MONTH(Enum):
        SHORT, FULL, NUM = "%b", "%B", "%m"

    class DAY(Enum):
        NUM, OF_YEAR = "%d", "%j"

    class HOUR(Enum):
        H24, H12, AM_PM = "%H", "%I", "%p"

    class MINUTE(Enum):
        NUM = "%M"

    class SECOND(Enum):
        NUM = "%S"

    class MICROSECOND(Enum):
        NUM = "%f"


class WeekDays(Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class DateTime(dt.datetime):
    nanosecond = 0
    FormatCode = FormatCode
    WeekDays = WeekDays

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([str(getattr(self, attr)) for attr in ['year', 'month', 'day', 'hour', 'minute', 'second'] if getattr(self, attr)])})"

    def __call__(self) -> dt.datetime:
        return dt.datetime.fromisoformat(self.isoformat())

    @staticmethod
    def today(**kwargs: Any) -> DateTime:
        return DateTime.from_date(dt.date.today())

    @classmethod
    def now(cls, tz: Any = None) -> DateTime:
        return cast(DateTime, super().now(tz=tz))

    @staticmethod
    def from_date(date: dt.date) -> DateTime:
        return DateTime.fromordinal(date.toordinal())  # type: ignore

    @staticmethod
    def from_datetime(datetime: dt.datetime) -> DateTime:
        return DateTime.fromisoformat(datetime.isoformat())  # type: ignore

    def casual_date(self, full_month: bool = False, day_first: bool = True, day_suffix: bool = False) -> str:
        day, month, year = self.Day.with_suffix if day_suffix else self.day, self.Month.full if full_month else self.Month.short, self.Year.full
        return " ".join((day, month, year) if day_first else (month, day, year))

    def isoformat_date(self, dashes: bool = True, reverse: bool = False) -> str:
        codes = (FormatCode.YEAR.WITH_CENTURY, FormatCode.MONTH.NUM, FormatCode.DAY.NUM)
        return self.strftime(f"{'-' if dashes else ''}".join(codes if not reverse else reversed(codes)))

    def filetag_date(self) -> str:
        return self.isoformat_date(dashes=False)

    def logformat(self) -> str:
        Code = FormatCode
        return self.strftime(f"[{Code.YEAR.WITH_CENTURY}-{Code.MONTH.NUM}-{Code.DAY.NUM} {Code.HOUR.H24}:{Code.MINUTE.NUM}:{Code.SECOND.NUM}:{Code.MICROSECOND.NUM}]")

    def delta(self, *args: Any, **kwargs: Any) -> "DateTime":
        return self.fromisoformat((self + relativedelta(*args, **kwargs)).isoformat())  # type: ignore

    @LazyProperty
    def TimeZone(self) -> TimeZone:
        return TimeZone(self)

    @LazyProperty
    def WeekDay(self) -> WeekDay:
        return WeekDay(self)

    @LazyProperty
    def Week(self) -> Week:
        return Week(self)

    @LazyProperty
    def Year(self) -> Year:
        return Year(self)

    @LazyProperty
    def Month(self) -> Month:
        return Month(self)

    @LazyProperty
    def Day(self) -> Day:
        return Day(self)

    @LazyProperty
    def Hour(self) -> Hour:
        return Hour(self)

    @LazyProperty
    def Minute(self) -> Minute:
        return Minute(self)

    @LazyProperty
    def Second(self) -> Second:
        return Second(self)

    @LazyProperty
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

    @LazyProperty
    def _suffixes(self) -> dict:
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
