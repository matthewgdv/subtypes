from __future__ import annotations

from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .date import Date
    from .time_ import Time
    from .datetime_ import DateTime

from .mixin import MetaInfoMixin


class DateAccessor:
    def __init__(self, date: Date) -> None:
        self._date = date


class TimeAccessor:
    def __init__(self, time: Union[Time, DateTime]) -> None:
        self._time = time


class WeekDayAccessor(DateAccessor):
    @property
    def short(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.SHORT)

    @property
    def full(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.FULL)

    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEKDAY.NUM)


class WeekAccessor(DateAccessor):
    @property
    def of_year_starting_monday(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEK.OF_YEAR_STARTING_MONDAY)

    @property
    def of_year_starting_sunday(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.WEEK.OF_YEAR_STARTING_SUNDAY)


class YearAccessor(DateAccessor):
    @property
    def without_century(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.YEAR.WITHOUT_CENTURY)

    @property
    def with_century(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.YEAR.WITH_CENTURY)


class MonthAccessor(DateAccessor):
    @property
    def short(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.SHORT)

    @property
    def full(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.FULL)

    @property
    def num(self) -> str:
        return self._date.strftime(MetaInfoMixin.FormatCode.MONTH.NUM)


class DayAccessor(DateAccessor):
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


class TimeZoneAccessor(TimeAccessor):
    @property
    def name(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.TIMEZONE.NAME)


class HourAccessor(TimeAccessor):
    @property
    def h24(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.HOUR.H24)

    @property
    def h12(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.HOUR.H12)

    @property
    def am_pm(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.HOUR.AM_PM)


class MinuteAccessor(TimeAccessor):
    @property
    def num(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.MINUTE.NUM)


class SecondAccessor(TimeAccessor):
    @property
    def num(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.SECOND.NUM)


class MicroSecondAccessor(TimeAccessor):
    @property
    def num(self) -> str:
        return self._time.strftime(MetaInfoMixin.FormatCode.MICROSECOND.NUM)
