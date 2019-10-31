from __future__ import annotations

import collections
from typing import List, Any, no_type_check
from collections.abc import Mapping, MutableSequence, Sequence

from .str import Str, RegexSettings

from maybe import Maybe


class RegexAccessor:
    """An accessor class for all regex-related Dict_ methods"""
    settings = RegexSettings()

    def __init__(self, parent: Dict_ = None) -> None:
        default = type(self).settings
        self.parent, self.settings = parent, RegexSettings(dotall=default.dotall, ignorecase=default.ignorecase, multiline=default.multiline)
        self.str = Str()

    def __call__(self, parent: Dict_ = None, settings: RegexSettings = None) -> RegexAccessor:
        self.parent, self.settings = Maybe(parent).else_(self.parent), Maybe(settings).else_(self.settings)
        return self

    def filter(self, regex: str) -> Dict_:
        """Remove any key-value pairs where the key is not a string, or where it is a string but doesn't match the given regex."""
        return type(self)({key: val for key, val in self.items() if isinstance(key, str) and self._str(key).re.search(regex) is not None})

    def get_all(self, regex: str, limit: int = None) -> List[Any]:
        """Return a list of all the values whose keys match the given regex."""
        vals = self.filter(regex)

        if limit is not None and len(vals) > limit:
            raise KeyError(f"Got {len(vals)} matches ({', '.join([repr(val) for val in vals])}). Expected at most {limit} matches.")
        else:
            return list(vals.values())

    def get_one(self, regex: str) -> Any:
        """Return the value whose key matches the given regex. KeyError will be raised if multiple matches are found."""
        return self.get_all(regex=regex, limit=1)[0]

    @classmethod
    def _str(cls, text: str) -> Str:
        return Str(text).re(settings=cls.settings).parent


class Dict_(collections.UserDict, dict):  # type: ignore
    """
    Subclass of the builtin 'dict' class with where inplace methods like dict.update() return self and therefore allow chaining.
    Also allows item access dynamically through attribute access. It recursively converts any mappings within itself into its own type.
    """
    data: dict
    re = RegexAccessor()
    dict_fields = {attr for attr in dir(dict()) if not attr.startswith("_")}

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.re = RegexAccessor(parent=self)

        for key, val in self.items():
            self[key] = val

    @no_type_check
    def update(self, item):
        """Same as dict.update(), but returns self and thus allows chaining."""
        self.data.update(item)
        return self

    @no_type_check
    def clear(self):
        """Same as dict.clear(), but returns self and thus allows chaining."""
        self.data.clear()
        return self

    def __setitem__(self, name: str, val: Any) -> None:
        clean_val = self._recursively_convert_mappings_to_own_type(val)

        super().__setitem__(name, clean_val)
        if isinstance(name, str) and name not in self.dict_fields and name.isidentifier():
            super().__setattr__(name, clean_val)

    def __delitem__(self, name: str) -> None:
        self.__delattr__(name)
        super().__delitem__(name)

    def __setattr__(self, name, val) -> None:
        self[name] = val

    def _recursively_convert_mappings_to_own_type(self, item) -> Any:
        if isinstance(item, Mapping) and not isinstance(item, type(self)):
            return type(self)(item)
        elif isinstance(item, (str, bytes)):
            return item
        elif isinstance(item, MutableSequence):
            for index, val in enumerate(item):
                item[index] = self._recursively_convert_mappings_to_own_type(val)
            return item
        elif isinstance(item, Sequence):
            try:
                return type(item)([self._recursively_convert_mappings_to_own_type(val) for val in item])
            except Exception:
                return tuple(self._recursively_convert_mappings_to_own_type(val) for val in item)
        else:
            return item
