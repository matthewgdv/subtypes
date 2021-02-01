from __future__ import annotations

from typing import Any, Type
from json import loads


class Translator:
    def __init__(self, translations: dict = None) -> None:
        self.translations = translations or {}

    def __call__(self, item: Any, recursive: bool = False) -> Any:
        return self.translate_recursively(item) if recursive else self.translate(item)

    def translate(self, item: Any) -> Any:
        return item if (constructor := self.translations.get(type(item))) is None else constructor(item)

    def translate_recursively(self, item: Any) -> Any:
        translated = self.translate(item)

        if isinstance(translated, list):
            for index, val in enumerate(translated):
                translated[index] = self.translate_recursively(val)
        elif isinstance(translated, dict):
            for key, val in translated.items():
                translated[key] = self.translate_recursively(val)

        return translated

    def translate_json(self, json: str, **kwargs: Any) -> Any:
        return self.translate(loads(json, **kwargs))


class TranslatableMeta(type):
    translator = Translator()

    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        cls.translator.translations.update({base: cls for base in cls.mro()[1:-1]})


class DoNotTranslateMeta(TranslatableMeta):
    def __init__(cls, name: str, bases: tuple, namespace: dict) -> None:
        pass
