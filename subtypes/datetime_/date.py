from __future__ import annotations

import datetime as dt
from typing import Any, Union

from dateutil.relativedelta import relativedelta

from subtypes import cached_property
from .mixin import MetaInfoMixin
from .accessor import YearAccessor, MonthAccessor, DayAccessor, WeekAccessor, WeekDayAccessor


class Date(dt.date, MetaInfoMixin):
    """
    A subclass of the stdlib time.date class with additional useful methods.
    All normal time attributes are shadowed by PascalCase attributes which have properties providing various string representations of that attribute.
    E.g. Date.today().WeekDayAccessor.full, or Date.today().YearAccessor.without_century
    """

    def __init__(self, year: int, month: int, day: int) -> None:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self}]"

    def __str__(self) -> str:
        return self.to_format(f"{self.FormatCode.YEAR.WITH_CENTURY}-{self.FormatCode.MONTH.NUM}-{self.FormatCode.DAY.NUM}")

    def shift(self, years: int = 0, months: int = 0, days: int = 0, weeks: int = 0) -> Date:
        """Add/subtract the given amount of time units (as keyword arguments) to this Date. E.g. Date.today().shift(days=-3, weeks=15)"""
        return self.from_date(self + relativedelta(years=years, months=months, days=days, weeks=weeks))

    def to_stdlib(self) -> dt.date:
        """Create the equivalent time.date object from this Date."""
        return dt.date.fromordinal(self.toordinal())

    def to_ordinal(self) -> int:
        return self.toordinal()

    def to_isoformat(self) -> str:
        """Create an isoformat date string from this Date."""
        return self.isoformat()

    def to_format(self, format_string: str) -> str:
        """Create a date string from this Date using a format string."""
        return self.strftime(format_string)

    def to_filetag(self) -> str:
        """Create a string suitable to be used as a date (not time!) tag within a filename."""
        return self.strftime(f"{self.FormatCode.YEAR.WITH_CENTURY}{self.FormatCode.MONTH.NUM}{self.FormatCode.DAY.NUM}")

    def to_casual(self, full_month: bool = False, day_first: bool = True, day_suffix: bool = False) -> str:
        """Create a human-readable time string from this DateTime with several options."""
        day, month, year = self.Day.with_suffix if day_suffix else self.day, self.Month.full if full_month else self.Month.short, self.Year.with_century
        return " ".join([str(item) for item in ((day, month, year) if day_first else (month, day, year))])

    @classmethod
    def today(cls, **kwargs: Any) -> Date:
        """Create a Date from today at midnight."""
        return cls.from_date(dt.date.today())

    @classmethod
    def from_date(cls, date: dt.date) -> Date:
        """Create a Date from a time.date object."""
        return cls(date.year, date.month, date.day)

    @classmethod
    def from_ordinal(cls, ordinal: int) -> Date:
        """Create a Date from a time.time object."""
        return cls.fromordinal(ordinal)

    @classmethod
    def from_isoformat(cls, date_string: str) -> Date:
        """Create a Date from an isoformat string."""
        return cls.fromisoformat(date_string)

    @classmethod
    def from_format(cls, date_string: str, format_string: str) -> Date:
        """Create a Date from a string representing a date and a format spec."""
        from .datetime_ import DateTime
        return DateTime.strptime(date_string, format_string).date()

    @classmethod
    def from_string(cls, text: str) -> Date:
        """Attempt to parse a string of text into a Date."""
        val, code = cls._calendar.parse(text)
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
    def WeekDay(self) -> WeekDayAccessor:
        return WeekDayAccessor(self)

    @cached_property
    def Week(self) -> WeekAccessor:
        return WeekAccessor(self)

    @cached_property
    def Year(self) -> YearAccessor:
        return YearAccessor(self)

    @cached_property
    def Month(self) -> MonthAccessor:
        return MonthAccessor(self)

    @cached_property
    def Day(self) -> DayAccessor:
        return DayAccessor(self)
