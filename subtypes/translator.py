from __future__ import annotations

from typing import Any, Dict, Type
from json import loads


class Translator:
    translations: dict[Type, Type] = {}
    default: Translator = None

    def __init__(self, translations: dict = None) -> None:
        self.translations = translations if translations is not None else self.translations.copy()

    def __call__(self, item: Any, recursive: bool = False) -> Any:
        return (self.translate_recursively if recursive else self.translate)(item)

    def translate(self, item: Any) -> Any:
        constructor = self.translations.get(type(item))
        return item if constructor is None else constructor(item)

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


Translator.default = Translator(translations=Translator.translations)
