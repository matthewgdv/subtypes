from __future__ import annotations

from typing import Any
import enum


class EnumMeta(enum.EnumMeta):
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


class BaseEnum(enum.Enum):
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
