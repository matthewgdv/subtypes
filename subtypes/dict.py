from __future__ import annotations

from typing import List, Any
from collections.abc import Mapping
import json

from django.utils.functional import cached_property as lazy_property

from .str import Str, Accessor
from .str import RegexAccessor as StrRegexAccessor
from .translator import Translator

from maybe import Maybe


class RegexAccessor(Accessor):
    """An accessor class for all regex-related Dict_ methods"""
    settings = StrRegexAccessor.Settings()

    def __init__(self, parent: Dict_ = None) -> None:
        default = type(self).settings
        self.parent, self.settings = parent, StrRegexAccessor.Settings(dotall=default.dotall, ignorecase=default.ignorecase, multiline=default.multiline)
        self.str = Str()

    def __call__(self, parent: Dict_ = None, dotall: bool = None, ignorecase: bool = None, multiline: bool = None) -> RegexAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        self.settings.dotall = Maybe(dotall).else_(self.settings.dotall)
        self.settings.ignorecase = Maybe(ignorecase).else_(self.settings.ignorecase)
        self.settings.multiline = Maybe(multiline).else_(self.settings.multiline)
        return self

    def filter(self, regex: str) -> Dict_:
        """Remove any key-value pairs where the key is not a string, or where it is a string but doesn't match the given regex."""
        return type(self.parent)(
            {key: val for key, val in self.parent.items()
             if isinstance(key, str) and Str(key).re(dotall=self.settings.dotall, ignorecase=self.settings.ignorecase, multiline=self.settings.multiline).search(regex) is not None}
        )

    def get_all(self, regex: str, limit: int = None) -> List[Any]:
        """Return a list of all the values whose keys match the given regex."""
        vals = self.filter(regex)

        if limit is not None and len(vals) > limit:
            raise KeyError(f"Got {len(vals)} matches: {', '.join([repr(val) for val in vals])}. Expected at most {limit} match(es).")
        else:
            return list(vals.values())

    def get_one(self, regex: str) -> Any:
        """Return the value whose key matches the given regex. KeyError will be raised if multiple matches are found."""
        return self.get_all(regex=regex, limit=1)[0]


class DictSettings:
    def __init__(self) -> None:
        self.re, self.dict_fields, self.translator, self.recursive = RegexAccessor.settings, {attr for attr in dir(dict()) if not attr.startswith("_")}, Translator.default, True


class Dict_(dict):
    """
    Subclass of the builtin 'dict' class with where inplace methods like dict.update() return self and therefore allow chaining.
    Also allows item access dynamically through attribute access. It recursively converts any dicts within itself into its own type.
    """
    settings = DictSettings()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if self.settings.recursive:
            for key, val in self.items():
                self[key] = val

    def __getitem__(self, name: str) -> Any:
        try:
            return super().__getitem__(name)
        except KeyError:
            default = type(self)()
            self[name] = default
            return default

    def __setitem__(self, name: str, val: Any) -> None:
        clean_val = self.settings.translator.translate(val)

        super().__setitem__(name, clean_val)
        if isinstance(name, str) and name not in self.settings.dict_fields and name.isidentifier():
            super().__setattr__(name, clean_val)

    def __delitem__(self, name: str) -> None:
        self.__delattr__(name)
        super().__delitem__(name)

    def __getattr__(self, name: str) -> Dict_:
        if (name.startswith("_") and name.endswith("_")):
            raise AttributeError(name)

        return self[name]

    def __setattr__(self, name, val) -> None:
        self[name] = val

    def __delattr__(self, name: str) -> None:
        del self[name]

    def __copy__(self) -> Dict_:
        return type(self)(super().__copy__())

    @lazy_property
    def re(self) -> RegexAccessor:
        return RegexAccessor(parent=self)

    def update(self, item: Mapping) -> Dict_:
        """Same as dict.update(), but returns self and thus allows chaining."""
        super().update(item)
        return self

    def clear(self) -> Dict_:
        """Same as dict.clear(), but returns self and thus allows chaining."""
        super().clear()
        return self

    def copy(self) -> Dict_:
        return type(self)(self.copy())

    def to_json(self, indent: int = 4, **kwargs: Any) -> str:
        return json.dumps(self, indent=indent, **kwargs)

    @classmethod
    def from_json(cls, json_string: str, **kwargs: Any) -> Dict_:
        item = json.loads(json_string, **kwargs)
        if isinstance(item, dict):
            return cls(item)
        else:
            raise TypeError(f"The following json string resolves to type '{type(item).__name__}', not type '{dict.__name__}':\n\n{json_string}")


Translator.translations[dict] = Dict_
