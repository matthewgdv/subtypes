from __future__ import annotations

import datetime as dt
from typing import Union

from subtypes import cached_property
from .mixin import MetaInfoMixin
from .accessor import TimeZoneAccessor, HourAccessor, MinuteAccessor, SecondAccessor, MicroSecondAccessor


class Time(dt.time, MetaInfoMixin):
    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, microsecond: int = 0,
                 tzinfo: dt.timezone = None, *, fold=0) -> None:
        pass

    @classmethod
    def from_time(cls, time: dt.time) -> Time:
        """Create a Time from a datetime.time object."""
        return cls(time.hour, time.minute, time.second, time.microsecond)

    @classmethod
    def from_isoformat(cls, time_string: str) -> Time:
        """Create a Time from an isoformat string."""
        return cls.fromisoformat(time_string)

    @classmethod
    def from_format(cls, time_string: str, format_string: str) -> Time:
        """Create a Time from a string representing a time and a format spec."""
        from .datetime_ import DateTime
        return DateTime.strptime(time_string, format_string).time()

    @classmethod
    def from_string(cls, text: str) -> Time:
        """Attempt to parse a string of text into a Time."""
        val, code = cls._calendar.parse(text)
        _, _, _, hour, minute, second, *_ = val

        if not (2 & code):
            raise ValueError(f"Could not parse stringlike value '{text}' to type '{cls.__name__}'.")

        return cls(hour, minute, second)

    @classmethod
    def infer(cls, datelike: Union[dt.datetime, dt.time, str]) -> Time:
        """Create a Time from a valid python object. Raises TypeError if an unsupported type is passed. Raises ValueError if an invalid instance of a supported type (like 'str' or 'int') is passed."""
        if isinstance(datelike, cls):
            return datelike
        elif isinstance(datelike, dt.datetime):
            return cls(datelike.hour, datelike.minute, datelike.second, datelike.microsecond)
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
