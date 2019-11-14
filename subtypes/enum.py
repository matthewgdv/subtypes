from __future__ import annotations

from typing import Any, List
import enum

import aenum


class EnumMeta(aenum.EnumMeta):
    def __repr__(cls) -> str:
        return f"{cls.__name__}[{', '.join([f'{member.name}={repr(member.value)}' for member in cls])}]"

    def __str__(cls) -> str:
        return f"{', '.join([repr(member.value) for member in cls])}"

    @property
    def names(cls) -> List[str]:
        """A list of the names in this Enum."""
        return [member.name for member in cls]

    @property
    def values(cls) -> List[Any]:
        """A list of the values in this Enum."""
        return [member.value for member in cls]

    def extend_enum(cls, name: str, value: Any) -> None:
        """Extend this Enum with an additional member created from the given name and value."""
        aenum.extend_enum(cls, name, value)

    def is_enum(cls, candidate: Any) -> bool:
        """Returns True if the candidate is a subclass of Enum, otherwise returns False."""
        try:
            return issubclass(candidate, enum.Enum)
        except TypeError:
            return False

    def raise_if_not_a_member(cls, value: Any) -> None:
        """Raises ValueError if the given value is not one of the values in this Enum, otherwise does nothing."""
        if value not in cls.values:
            raise ValueError(f"Invalid {cls.__name__} '{value}', must be one of {cls}.")


class ValueEnumMeta(EnumMeta):
    def __getattribute__(cls, name: str) -> Any:
        value = super().__getattribute__(name)

        if isinstance(value, cls):
            value = value.value

        return value


class Enum(aenum.Enum, metaclass=EnumMeta):
    """A subclass of aenum.Enum with additional methods. Attribute access on descendants of this class returns the value corresponding to that name, rather than returning the member."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name}, value={repr(self.value)})"

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Any) -> bool:
        return other is self or other == self.value

    def __ne__(self, other: Any) -> bool:
        return other is not self and other != self.value

    def __str__(self) -> str:
        return str(self.value)


class ValueEnum(aenum.Enum, metaclass=ValueEnumMeta):
    pass


class AutoEnum(Enum):
    """Automatically use _generate_next_value_ when values are missing"""
    _settings_ = aenum.AutoValue

    def _generate_next_value_(name: str, start: str, count: str, last_values: List[str]) -> str:
        return name.lower()


class ValueAutoEnum(AutoEnum, metaclass=ValueEnumMeta):
    pass
