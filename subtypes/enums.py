from __future__ import annotations

from typing import Any, List
import enum

import aenum


class EnumMeta(aenum.EnumMeta):
    # Implementation of EnumMeta.__new__() and EnumMeta.__prepare__() alongside subtypes.Enum inheriting from enum.Enum unnecessarily
    # when it already inherits from aenum.Enum which is a subclass of enum.Enum, is done so that the goddamn PyCharm type checker
    # is satisfied that subtypes.Enum is, in fact, a freaking enumeration. Otherwise it just doesn't get it.

    def __new__(mcs, name: str, bases: tuple, namespace: dict, init: Any = None, start: Any = None, settings: tuple = ()) -> EnumMeta:
        if enum.Enum in bases:
            bases = tuple(base for base in bases if not base == enum.Enum)

        return super().__new__(mcs, name, bases, namespace, init, start, settings)

    @classmethod
    def __prepare__(mcs, name: str, bases: tuple, init: Any = None, start: Any = None, settings: tuple = ()) -> EnumMeta:
        if enum.Enum in bases:
            (bases := list(bases)).remove(enum.Enum)
            bases = tuple(bases)

        return super().__prepare__(name, bases, init, start, settings)

    def __repr__(cls) -> str:
        return f"{cls.__name__}[{', '.join([f'{member.name}={repr(member.value)}' for member in cls])}]"

    def __str__(cls) -> str:
        return cls.__name__

    def __call__(cls, *args: Any, **kwargs: Any):
        try:
            return super().__call__(*args, **kwargs)
        except ValueError as ex:
            msg, = ex.args
            raise ValueError(f"{msg}, must be one of: {', '.join([repr(member.value) for member in cls])}.")

    @property
    def names(cls) -> list[str]:
        """A list of the names in this Enum."""
        return [member.name for member in cls]

    @property
    def values(cls) -> list[Any]:
        """A list of the values in this Enum."""
        return [member.value for member in cls]

    def extend(cls, name: str, value: Any) -> None:
        """Extend this Enum with an additional member created from the given name and value."""
        aenum.extend_enum(cls, name, value)

    def is_enum(cls, candidate: Any) -> bool:
        """Returns True if the candidate is a subclass of Enum, otherwise returns False."""
        try:
            return issubclass(candidate, enum.Enum)
        except TypeError:
            return False


class ValueEnumMeta(EnumMeta):
    def __getattribute__(cls, name: str) -> Any:
        value = super().__getattribute__(name)

        if isinstance(value, cls):
            value = value.value

        return value


class BaseEnum(aenum.Enum):
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

    def map_to(self, mapping: dict, else_: Any = None, raise_for_failure: bool = True) -> Any:
        if (ret := mapping.get(self, else_)) is None and raise_for_failure:
            raise ValueError(f"No mapping for '{self}' found in {mapping}.")

        return ret


class Enum(BaseEnum, enum.Enum, metaclass=EnumMeta):
    """A subclass of aenum.Enum with additional methods."""


class ValueEnum(BaseEnum, metaclass=ValueEnumMeta):
    """A subclass of subtypes.Enum. Attribute access on descendants of this class returns the value corresponding to that name, rather than returning the member."""


class BaseAutoEnum(aenum.Enum):
    _settings_ = aenum.AutoValue

    def _generate_next_value_(name: str, start: str, count: str, last_values: list[str]) -> str:
        return name.lower()


class AutoEnum(Enum, BaseAutoEnum):
    """A subclass of subtypes.Enum. Automatically uses _generate_next_value_ when values are missing"""


class ValueAutoEnum(BaseEnum, BaseAutoEnum, metaclass=ValueEnumMeta):
    """A subclass of subtypes.ValueEnum. Missing values are automatically supplied by _generate_next_value_."""
