from __future__ import annotations

from typing import Any, List
import enum

import aenum


class EnumMeta(aenum.EnumMeta):
    def __repr__(cls) -> str:
        return f"{cls.__name__}[{', '.join([f'{member.name}={repr(member.value)}' for member in cls])}]"

    def __str__(cls) -> str:
        return f"{', '.join([repr(member.value) for member in cls])}"

    def __getattribute__(cls, name: str) -> Any:
        value = super().__getattribute__(name)

        if isinstance(value, cls):
            value = value.value

        return value

    @property
    def names(cls) -> List[str]:
        return [member.name for member in cls]

    @property
    def values(cls) -> List[Any]:
        return [member.value for member in cls]

    def extend_enum(cls, name: str, value: Any) -> None:
        aenum.extend_enum(cls, name, value)

    def is_enum(cls, candidate: Any) -> bool:
        try:
            return issubclass(candidate, enum.Enum)
        except TypeError:
            return False

    def raise_if_not_a_member(cls, value: Any) -> None:
        if value not in cls.values:
            raise ValueError(f"Invalid {cls.__name__} '{value}', must be one of {cls}.")


class Enum(aenum.Enum, metaclass=EnumMeta):
    def __repr__(self) -> str:
        return f"{type(self).__name__}(name={self.name}, value={repr(self.value)})"

    def __str__(self) -> str:
        return str(self.value)
