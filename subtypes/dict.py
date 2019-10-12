from __future__ import annotations

import collections
from typing import List, Any, no_type_check

from .str import Str


class Dict_(collections.UserDict, list):  # type: ignore
    """Subclass of the builtin 'dict' class with additional useful methods. All the 'dict' class inplace methods return self and therefore allow chaining when called from this class."""
    data: dict

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

    def filter_re(self, regex: str) -> Dict_:
        """Remove any key-value pairs where the key is not a string, or where it is a string but doesn't match the given regex."""
        return type(self)({key: val for key, val in self.items() if isinstance(key, str) and Str(key).re.search(regex) is not None})

    def get_re(self, regex: str, limit: int = None) -> List[Any]:
        """Return a list of all the values whose keys match the given regex."""
        vals = self.filter_re(regex)

        if limit is not None and len(vals) > limit:
            raise KeyError(f"Got {len(vals)} matches ({', '.join([repr(val) for val in vals])}). Expected at most {limit} matches.")
        else:
            return list(vals.values())

    def getone_re(self, regex: str) -> Any:
        """Return the value whose key matches the given regex. KeyError will be raised if multiple matches are found."""
        return self.get_re(regex=regex, limit=1)[0]
