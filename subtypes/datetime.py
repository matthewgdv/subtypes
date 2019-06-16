from __future__ import annotations

import datetime as dt
from typing import Any, cast

from dateutil.relativedelta import relativedelta

from .enum import Enum


class DateTime(dt.datetime):
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

    def month_name(self, full_name: bool = True) -> str:
        return self.strftime("%B") if full_name else self.strftime("%b")

    def day_suffix(self) -> str:
        suffixes = {day: suffix for days, suffix in [([1, 21, 31], "st"), ([2, 22], "nd"), ([3, 23], "rd")] for day in days}
        return suffixes.get(self.day, "th")

    def get_human_date(self, full_month: bool = False, day_first: bool = True, day_suffix: bool = False) -> str:
        day_clean = f"{self.day}{self.day_suffix() if day_suffix else ''}"
        month_clean = f"{self.month_name(full_name=full_month)}"
        date = f"{day_clean} {month_clean} {self.year}" if day_first else f"{self.year} {month_clean} {day_clean}"
        return date

    def isoformat_date(self, dashes: bool = True, year_first: bool = True) -> str:
        ordering = (self.year, self.month, self.day) if year_first else (self.day, self.month, self.year)
        return f"{'-' if dashes else ''}".join([self._pad_integer_with_zeroes(val, 2) for val in ordering])

    def date_tag(self) -> str:
        return self.isoformat_date(dashes=False)

    def get_timestamp(self) -> str:
        hours_minutes_seconds = ":".join([self._pad_integer_with_zeroes(num, 2) for num in (self.hour, self.minute, self.second)])
        return f"[{self.isoformat_date(dashes=True)} {hours_minutes_seconds}:{self._pad_integer_with_zeroes(self.microsecond, 6, False)}]"

    def delta(self, *args: Any, **kwargs: Any) -> "DateTime":
        return self.fromisoformat((self + relativedelta(*args, **kwargs)).isoformat())  # type: ignore

    @staticmethod
    def _pad_integer_with_zeroes(num: int, desired_len: int, left_side: bool = True) -> str:
        missing_zeroes = "0"*(desired_len - len(str(num)))
        return f"{missing_zeroes}{num}" if left_side else f"{num}{missing_zeroes}"

    class WeekDays(Enum):
        Monday = "monday"
        Tuesday = "tuesday"
        Wednesday = "wednesday"
        Thursday = "thursday"
        Friday = "friday"
        Saturday = "saturday"
        Sunday = "sunday"
