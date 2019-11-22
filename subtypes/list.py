from __future__ import annotations

from typing import Any, Dict, Iterable, List
import json

from django.utils.functional import cached_property as lazy_property

from maybe import Maybe

from .str import Accessor, Settings
from .translator import Translator


class SliceAccessor(Accessor):
    """An accessor class for all slicing-related Str methods"""

    class Settings(Settings):
        def __init__(self, raise_if_absent: bool = False) -> None:
            self.raise_if_absent = raise_if_absent

    settings = Settings()

    def __init__(self, parent: List_ = None) -> None:
        self.parent, self.settings = parent, self.Settings(raise_if_absent=type(self).settings.raise_if_absent)

    def __call__(self, parent: List_ = None, raise_if_absent: bool = None) -> SliceAccessor:
        self.parent, self.settings.raise_if_absent = Maybe(parent).else_(self.parent), Maybe(raise_if_absent).else_(self.settings.raise_if_absent)
        return self

    def before(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ before the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]])

    def before_first(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ before the first instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]])

    def before_last(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ before the last instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[-1]])

    def after(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ after the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]+1:])

    def after_first(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ after the first instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]+1:])

    def after_last(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ after the last instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[-1]+1:])

    def from_(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ from the given value onwards, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]:])

    def from_first(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ from the first instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]:])

    def from_last(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ from the last instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[-1]:])

    def until(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ until the given value, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]+1])

    def until_first(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ until the first instance of the given value (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]+1])

    def until_last(self, value: Any) -> List_:
        """Return all elements (if any) in the List_ until the last instance of the given value (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[-1]+1])

    def _slice_helper(self, value: Any, multiple_matches_forbidden: bool) -> List[int]:
        matches = [index for index, val in enumerate(self.parent) if val == value]

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise ValueError(f"Too many matches, return value would be ambigous (Expected 1, got {len(matches)}).")

        if self.settings.raise_if_absent and not matches:
            raise ValueError(f"'{value}' could not be found in '{self.parent}'.")

        return matches


class ListSettings(Settings):
    def __init__(self) -> None:
        self.slice, self.translator, self.recursive = SliceAccessor(), Translator.default, True


class List_(list):  # type: ignore
    """Subclass of the builtin 'list' class with additional useful methods. All the 'list' class inplace methods return self and therefore allow chaining when called from this class."""
    settings = ListSettings()

    def __init__(self, iterable: Iterable = None) -> None:
        super().__init__(iterable)

        if self.settings.recursive:
            for index, val in enumerate(self):
                self[index] = self.settings.translator.translate(val)

    def __add__(self, other: list) -> List_:
        return type(self)(super().__add__(other))

    def __radd__(self, other: list) -> List_:
        return type(self)(super().__radd__(other))

    def __iadd__(self, other):
        super().__iadd__(other)
        return self

    def __mul__(self, n: int) -> List_:
        return type(self)(super().__mul__(n))

    def __rmul__(self, n: int) -> List_:
        return type(self)(super().__rmul__(n))

    def __imul__(self, n: int) -> List_:
        super().__imul__(n)
        return self

    def __copy__(self):
        return type(self)(super().__copy__())

    @lazy_property
    def slice(self) -> SliceAccessor:
        return SliceAccessor(parent=self)

    def append(self, item: Any) -> List_:
        """Same as list.append(), but returns self and thus allows chaining."""
        super().append(item)
        return self

    def extend(self, item: Any) -> List_:
        """Same as list.extend(), but returns self and thus allows chaining."""
        super().extend(item)
        return self

    def insert(self, index: int, item: Any) -> List_:
        """Same as list.insert(), but returns self and thus allows chaining."""
        super().insert(index, item)
        return self

    def remove(self, item: Any) -> List_:
        """Same as list.remove(), but returns self and thus allows chaining."""
        super().remove(item)
        return self

    def reverse(self) -> List_:
        """Same as list.reverse(), but returns self and thus allows chaining."""
        super().reverse()
        return self

    def sort(self) -> List_:
        """Same as list.sort(), but returns self and thus allows chaining."""
        super().sort()
        return self

    def clear(self) -> List_:
        """Same as list.clear(), but returns self and thus allows chaining."""
        super().clear()
        return self

    def copy(self):
        return type(self)(self)

    def flatten(self, exclude_strings: bool = True) -> List_:
        """Recursively traverses any iterables within this List_ and unpacks them in order into a new flat List_."""
        def recurse(iterable: Iterable, output: list, exclude_strings: bool) -> None:
            for item in iterable:
                if hasattr(item, "__iter__") and (not isinstance(item, str) or not exclude_strings):
                    recurse(iterable=item, output=output, exclude_strings=exclude_strings)
                else:
                    output.append(item)

        new_data: list = []
        recurse(iterable=self, output=new_data, exclude_strings=exclude_strings)
        return type(self)(new_data)

    def align_nested_strings(self, fieldsep: str = ",", linesep: str = "\n", tabsize: int = 4, tabs: bool = False) -> str:
        """Align nested iterables of strings to return a string such that the strings at each index position align with each other."""
        def calculate_tabs_needed(this_len: int, max_len: int, tab_size: int = 4) -> int:
            return ((max_len // tab_size) + 1) - (this_len // tab_size)

        def calculate_spaces_needed(this_len: int, max_len: int, tab_size: int = 4) -> int:
            return ((calculate_tabs_needed(this_len, max_len, tab_size) - 1) * tab_size) + (tab_size - (this_len % tab_size))

        def calculate_tabs_or_spaces_needed(strings: List[str], tab_size: int = 4, with_tabs: bool = True) -> Dict[int, int]:
            max_len = max([len(text) for text in strings])
            return {index: ((calculate_tabs_needed if with_tabs else calculate_spaces_needed)(len(text), max_len, tab_size)) for index, text in enumerate(strings)}

        if not self:
            return ""

        if not all([len(sublist) == len(self[0]) for sublist in self[1:]]):
            raise ValueError(f"All sublists must be the same length. The current breakdown is:\n\n{[len(sub) for sub in self]}\n\nThe sublists are:\n\n{self}")

        delimiter = "\t" if tabs else " "
        indices = range(len(self[0]))

        with_seps = [[text if index == (len(sublist) - 1) else f"{text}{fieldsep}" for index, text in enumerate(sublist)] for sublist in self]
        tab_sizes = {index: calculate_tabs_or_spaces_needed([sublist[index] for sublist in with_seps], with_tabs=tabs, tab_size=tabsize) for index in indices}
        adjusted = [[f"{with_seps[num][index]}{tab_sizes[index][num] * delimiter}" for index in indices] for num in range(len(with_seps))]

        return f"{linesep}".join(["".join(sublist).rstrip() for sublist in adjusted])

    def to_json(self, indent: int = 4, **kwargs: Any) -> str:
        return json.dumps(self, indent=indent, **kwargs)

    @classmethod
    def from_json(cls, json_string: str, **kwargs: Any) -> List_:
        item = json.loads(json_string, **kwargs)
        if isinstance(item, list):
            return cls(item)
        else:
            raise TypeError(f"The following json string resolves to type '{type(item).__name__}', not type '{list.__name__}':\n\n{json_string}")


Translator.translations[list] = List_
