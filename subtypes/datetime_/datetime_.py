from __future__ import annotations

import datetime as dt
from typing import Union

from dateutil.relativedelta import relativedelta

from functools import cached_property
from .date import Date
from .time_ import Time
from .accessor import TimeZoneAccessor, HourAccessor, MinuteAccessor, SecondAccessor, MicroSecondAccessor


class DateTime(Date, dt.datetime):
    """
    A subclass of the stdlib time.time class with additional useful methods.
    All normal time attributes are shadowed by PascalCase attributes which have properties providing various string representations of that attribute.
    E.g. DateTime.now().WeekDayAccessor.full, or DateTime.now().YearAccessor.without_century
    """
    nanosecond = 0

    def __init__(self, year: int, month: int, day: int,
                 hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 tzinfo: dt.timezone = None, *, fold=0) -> None:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self}]"

    def __str__(self) -> str:
        text = f"{self.FormatCode.YEAR.WITH_CENTURY}-{self.FormatCode.MONTH.NUM}-{self.FormatCode.DAY.NUM} {self.FormatCode.HOUR.H24}:{self.FormatCode.MINUTE.NUM}:{self.FormatCode.SECOND.NUM}"

        if self.tzinfo is not None:
            text = f"{text} | {self.tzinfo.tzname(None)}"

        return self.to_format(text)

    def shift(self, years: int = 0, months: int = 0, days: int = 0, weeks: int = 0,
              hours: int = 0, minutes: int = 0, seconds: int = 0, microseconds: int = 0) -> DateTime:
        """Add/subtract the given amount of time units (as keyword arguments) to this DateTime. E.g. DateTime.now().shift(days=-3, hours=15)"""
        return self.from_datetime((self + relativedelta(years=years, months=months, days=days, weeks=weeks,
                                                        hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)))

    def date(self) -> Date:
        """Create the equivalent time.date object from this DateTime."""
        return Date(self.year, self.month, self.day)

    def time(self) -> Time:
        """Create the equivalent time.date object from this DateTime."""
        return Time(self.hour, self.minute, self.second, self.microsecond)

    def to_stdlib(self) -> dt.datetime:
        """Create the equivalent time.time object from this DateTime."""
        return dt.datetime.fromordinal(self.toordinal())

    def to_isoformat(self, sep: str = " ", timespec: str = "auto") -> str:
        return self.isoformat(sep=sep, timespec=timespec)

    def to_format(self, format_string: str) -> str:
        """Create a time string from this DateTime using a format string."""
        return self.strftime(format_string)

    @classmethod
    def from_datetime(cls, datetime: dt.datetime) -> DateTime:
        """Create a DateTime from a time.time object."""
        return cls(datetime.year, datetime.month, datetime.day, datetime.hour, datetime.minute, datetime.second, datetime.microsecond)

    @classmethod
    def from_isoformat(cls, date_string: str) -> DateTime:
        """Create a DateTime from an isoformat string."""
        return cls.from_datetime(dt.datetime.fromisoformat(date_string))

    @classmethod
    def from_format(cls, date_string: str, format_string: str) -> DateTime:
        """Create a DateTime from a string representing a time and a format spec."""
        return cls.strptime(date_string, format_string)

    @classmethod
    def from_string(cls, text: str) -> DateTime:
        """Attempt to parse a string of text into a DateTime."""
        val, code = cls._calendar.parse(text)
        year, month, day, hour, minute, second, *_ = val

        if not (1 & code):
            raise ValueError(f"Could not parse stringlike value '{text}' to type '{cls.__name__}'.")

        return cls(year, month, day, hour, minute, second)

    @classmethod
    def from_parts(cls, date: Date, time: Time, tzinfo: dt.timezone = None) -> DateTime:
        return cls.combine(date=date, time=time, tzinfo=tzinfo)

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
            try:
                return cls.fromtimestamp(datelike)
            except OSError:
                return cls.fromtimestamp(datelike//1000)

        elif isinstance(datelike, str):
            try:
                return cls.from_isoformat(datelike)
            except ValueError:
                return cls.from_string(datelike)
        else:
            raise TypeError(f"Unsupported type '{type(datelike)}' for inference to type '{cls.__name__}'.")

    @cached_property
    def TimeZone(self) -> TimeZoneAccessor:
        return TimeZoneAccessor(self)

    @cached_property
    def Hour(self) -> HourAccessor:
        return HourAccessor(self)

    @cached_property
    def Minute(self) -> MinuteAccessor:
        return MinuteAccessor(self)

    @cached_property
    def Second(self) -> SecondAccessor:
        return SecondAccessor(self)

    @cached_property
    def MicroSecond(self) -> MicroSecondAccessor:
        return MicroSecondAccessor(self)
