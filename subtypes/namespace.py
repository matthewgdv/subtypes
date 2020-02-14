from __future__ import annotations

from typing import Any, Iterator, Tuple


class NameSpace:
    """A namespace class that allows attribute access dynamically through item access."""

    def __init__(self, mapping: dict = None, /, **kwargs: Any) -> None:
        self(mapping, **kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self])})"

    def __call__(self, mapping: dict = None, /, **kwargs: Any) -> NameSpace:
        for name, _ in self:
            del self[name]

        if mapping is not None:
            vars(self).update(mapping)

        vars(self).update(kwargs)

        return self

    def __len__(self) -> int:
        return len([item for item in self])

    def __getitem__(self, name: str) -> Any:
        return getattr(self, name if name is not None else "__none__")

    def __setitem__(self, name: str, val: Any) -> None:
        setattr(self, name if val is not None else "__none__", val)

    def __delitem__(self, name: str) -> None:
        delattr(self, name if name is not None else "__none__")

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        return iter([(name, val) for name, val in vars(self).items() if not name.startswith("_")])

    def __contains__(self, other: Any) -> bool:
        return other in set(vars(self).keys())
