from __future__ import annotations

from typing import Any

import aenum


class EnumMeta(aenum.EnumMeta):
    def __repr__(self) -> str:
        return f"{self.__name__}({', '.join([repr(member) for member in self])})"

    def __str__(self) -> str:
        return f"{', '.join([member.value for member in self])}"

    def __getattribute__(cls, name: str) -> Any:
        value = super().__getattribute__(name)

        if isinstance(value, cls):
            value = value.value

        return value

    def extend_enum(cls, name: str, value: Any) -> EnumMeta:
        aenum.extend_enum(cls, name, value)


class Enum(aenum.Enum, metaclass=EnumMeta):
    def __repr__(self) -> str:
        return f"[{self.name}: {repr(self.value)}]"
