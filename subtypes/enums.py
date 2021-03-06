from __future__ import annotations

from typing import Any
import enum


class EnumMeta(enum.EnumMeta):
    class Auto:
        def __repr__(self) -> str:
            return type(self).__name__

    class Alias:
        def __init__(self, value: Any = None) -> None:
            self.value = value

        def __repr__(self) -> str:
            return f"{type(self).__name__}(value={self.value})"

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        new_namespace = enum._EnumDict()
        aliases: dict[EnumMeta.Alias, enum.auto] = {}

        for key, val in namespace.items():
            if isinstance(val, mcs.Auto):
                new_namespace[key] = enum.auto()
            elif isinstance(val, mcs.Alias):
                new_namespace[key] = aliases.setdefault(val, enum.auto() if val.value is None else val.value)
            else:
                new_namespace[key] = val

        return super().__new__(mcs, name, bases, new_namespace)

    def __repr__(cls) -> str:
        return f"{cls.__name__}({', '.join([f'{member.name}={repr(member.value)}' for member in cls])})"

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


class Enum(enum.Enum, metaclass=EnumMeta):
    """A subclass of enum.Enum with additional methods."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.name}]"

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Any) -> bool:
        return other is self or other == self.name

    def __ne__(self, other: Any) -> bool:
        return other is not self and other != self.name

    def __str__(self) -> str:
        return str(self.key)

    def map_to(self, mapping: dict, else_: Any = None, raise_for_failure: bool = True) -> Any:
        if (ret := mapping.get(self, else_)) is None and raise_for_failure:
            raise ValueError(f"No mapping for '{self}' found in {mapping}.")

        return ret
