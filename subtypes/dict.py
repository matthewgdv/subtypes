from __future__ import annotations

from typing import Any, Callable
from collections.abc import Mapping
import json

from .str import Str, Accessor
from .str import RegexAccessor as StrRegexAccessor, Settings
from .translator import TranslatableMeta, DoNotTranslateMeta

from maybe import Maybe


dict_fields = {attr for attr in dir(dict()) if not attr.startswith("_")}


def is_valid_for_attribute_actions(name: Any) -> bool:
    return isinstance(name, str) and name not in dict_fields and name.isidentifier()


class AccessError(KeyError, AttributeError):
    pass


class RegexAccessor(Accessor):
    """An accessor class for all regex-related Dict methods"""

    def __init__(self, parent: Dict = None) -> None:
        self.parent, self.settings = parent, StrRegexAccessor.Settings()

    def __call__(self, parent: Dict = None, dotall: bool = None, ignorecase: bool = None, multiline: bool = None) -> RegexAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        self.settings.dotall = Maybe(dotall).else_(self.settings.dotall)
        self.settings.ignorecase = Maybe(ignorecase).else_(self.settings.ignorecase)
        self.settings.multiline = Maybe(multiline).else_(self.settings.multiline)
        return self

    def filter(self, regex: str) -> Dict:
        """Remove any key-value pairs where the key is not a string, or where it is a string but doesn't match the given regex."""
        return type(self.parent)(
            {key: val for key, val in self.parent.items()
             if isinstance(key, str) and Str(key).re(dotall=self.settings.dotall, ignorecase=self.settings.ignorecase, multiline=self.settings.multiline).search(regex) is not None}
        )

    def get_all(self, regex: str, limit: int = None) -> list[Any]:
        """Return a list of all the values whose keys match the given regex."""
        vals = self.filter(regex)

        if limit is not None and len(vals) > limit:
            raise KeyError(f"Got {len(vals)} matches: {', '.join([repr(val) for val in vals])}. Expected at most {limit} match(es).")
        else:
            return list(vals.values())

    def get_one(self, regex: str) -> Any:
        """Return the value whose key matches the given regex. KeyError will be raised if multiple matches are found."""
        return self.get_all(regex=regex, limit=1)[0]


class BaseDict(dict):
    """
    An alternative implementation of collections.UserDict that inherits directly from 'dict'. All the 'dict' class inplace methods return self and therefore allow chaining when called from this class.
    """

    def update(self, item: Mapping = None, **kwargs) -> BaseDict:
        """Same as dict.update(), but returns self and thus allows chaining."""
        super().update(item)
        return self

    def clear(self) -> BaseDict:
        """Same as dict.clear(), but returns self and thus allows chaining."""
        super().clear()
        return self

    def copy(self) -> BaseDict:
        return type(self)(self)


class Dict(BaseDict, metaclass=TranslatableMeta):
    """
    Subclass of the builtin 'dict' class with where inplace methods like dict.update() return self and therefore allow chaining.
    Also allows item access dynamically through attribute access. It recursively converts any str, list, and dict instances into Str, List, and Dict.
    """

    class Accessors(Settings):
        re = RegexAccessor

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        for key, val in self.items():
            self[key] = val

    def __getitem__(self, name: str) -> Any:
        try:
            return super().__getitem__(name)
        except KeyError:
            self[name] = default = self._factory_(name=name)
            return default

    def __setitem__(self, name: str, val: Any) -> None:
        clean_val = type(self).translator.translate(val)
        super().__setitem__(name, clean_val)

        if is_valid_for_attribute_actions(name):
            super().__setattr__(name, clean_val)

    def __delitem__(self, name: str) -> None:
        super().__delitem__(name)

        if is_valid_for_attribute_actions(name):
            super().__delattr__(name)

    def __getattr__(self, name: str) -> Dict:
        return self[name]

    def __setattr__(self, name: str, val: Any) -> None:
        if name in dict_fields:
            raise AttributeError(f"Cannot assign to attribute '{type(self).__name__}.{name}'.")

        if name.startswith("_") and name.endswith("_"):
            super().__setattr__(name, val)
        else:
            self[name] = val

    def __delattr__(self, name: str) -> None:
        if name in dict_fields:
            raise AttributeError(f"Cannot delete attribute '{type(self).__name__}.{name}'.")

        if name.startswith("_") and name.endswith("_"):
            super().__delattr__(name)
        else:
            del self[name]

    def _factory_(self, name: str) -> Dict:
        raise AccessError(f"'{name}' not found in {type(self).__name__}: {self}")

    def setdefault_lazy(self, key: Any, factory: Callable = None, pass_key: bool = False) -> Any:
        if (val := self.get(key, AccessError)) is AccessError:
            self[key] = val = factory(key) if pass_key else factory()

        return val

    @property
    def re(self) -> RegexAccessor:
        return self.Accessors.re(parent=self)

    def to_json(self, indent: int = 4, **kwargs: Any) -> str:
        return json.dumps(self, indent=indent, **kwargs)

    @classmethod
    def from_json(cls, json_string: str, **kwargs: Any) -> Dict:
        if isinstance((item := json.loads(json_string, **kwargs)), dict):
            return cls(item)
        else:
            raise TypeError(f"The following json string resolves to type '{type(item).__name__}', not type '{dict.__name__}':\n\n{json_string}")


class DefaultDict(Dict, metaclass=DoNotTranslateMeta):
    def _factory_(self, name: str) -> DefaultDict:
        return type(self)()
