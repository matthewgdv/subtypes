from __future__ import annotations

from typing import NoReturn


class SingletonMeta(type):
    def __repr__(cls) -> str:
        return cls.__name__

    def __call__(cls) -> NoReturn:  # type: ignore
        raise TypeError(f"Singleton class {cls.__name__} is not callable.")


class Singleton(metaclass=SingletonMeta):
    pass
