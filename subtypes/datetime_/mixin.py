from __future__ import annotations

import parsedatetime

from subtypes import Enum


class MetaInfoMixin:
    _calendar = parsedatetime.Calendar()

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
