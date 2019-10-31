from __future__ import annotations

from typing import Any


class NameSpace:
    """A namespace class that allows attribute access dynamically through item access."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) > 1:
            raise TypeError(f"{type(self).__name__} only accepts a single positional argument (of type collections.Mapping).")
        else:
            mappings = {} if not len(args) else args[0]

        self.__dict__.update({**mappings, **kwargs})

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self])})"

    def __len__(self) -> int:
        return len([item for item in self])

    def __getitem__(self, name: str) -> Any:
        return getattr(self, name)

    def __setitem__(self, name: str, val: Any) -> None:
        setattr(self, name, val)

    def __delitem__(self, name: str) -> None:
        self.__delattr__(name)

    def __iter__(self) -> NameSpace:
        return iter({name: val for name, val in vars(self).items() if not name.startswith("_")}.items())

    def __contains__(self, other: Any) -> bool:
        return other in set(vars(self).keys())

    def _clear(self) -> None:
        for name, item in self:
            del self[name]
