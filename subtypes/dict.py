from __future__ import annotations

import collections
from typing import List, Any, no_type_check

from .str import Str


class Dict_(collections.UserDict, list):  # type: ignore
    data: dict

    @no_type_check
    def update(self, item):
        self.data.update(item)
        return self

    @no_type_check
    def clear(self):
        self.data.clear()
        return self

    def filter_re(self, regex: str) -> dict:
        return type(self)({key: val for key, val in self.items() if isinstance(key, str) and Str(key).re.search(regex) is not None})

    def get_re(self, regex: str, limit: int = None) -> List[Any]:
        vals = self.filter_re(regex)

        if limit is not None and len(vals) > limit:
            raise KeyError(f"Got {len(vals)} matches ({', '.join([repr(val) for val in vals])}). Expected at most {limit} matches.")
        else:
            return list(vals.values())

    def getone_re(self, regex: str) -> Any:
        return self.get_re(regex=regex, limit=1)[0]
