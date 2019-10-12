from __future__ import annotations

import collections
from typing import Any, Dict, Iterable, List, no_type_check


class List_(collections.UserList, list):  # type: ignore
    """Subclass of the builtin 'list' class with additional useful methods. All the 'list' class inplace methods return self and therefore allow chaining when called from this class."""
    data: list

    @no_type_check
    def append(self, item):
        """Same as list.append(), but returns self and thus allows chaining."""
        self.data.append(item)
        return self

    @no_type_check
    def extend(self, item):
        """Same as list.extend(), but returns self and thus allows chaining."""
        self.data.extend(item)
        return self

    @no_type_check
    def insert(self, index, item):
        """Same as list.insert(), but returns self and thus allows chaining."""
        self.data.insert(index, item)
        return self

    @no_type_check
    def remove(self, item):
        """Same as list.remove(), but returns self and thus allows chaining."""
        self.data.remove(item)
        return self

    @no_type_check
    def reverse(self):
        """Same as list.reverse(), but returns self and thus allows chaining."""
        self.data.reverse()
        return self

    @no_type_check
    def sort(self):
        """Same as list.sort(), but returns self and thus allows chaining."""
        self.data.sort()
        return self

    @no_type_check
    def clear(self):
        """Same as list.clear(), but returns self and thus allows chaining."""
        self.data.clear()
        return self

    def flatten(self, exclude_strings: bool = True) -> List_:
        """Recursively traverses any iterables within this List_ and unpacks them in order into a new flat List_."""
        def recurse(iterable: Iterable, output: list, exclude_strings: bool) -> None:
            for item in iterable:
                if hasattr(item, "__iter__") and (not isinstance(item, str) or not exclude_strings):
                    recurse(iterable=item, output=output, exclude_strings=exclude_strings)
                else:
                    output.append(item)

        new_data: list = []
        recurse(iterable=self.data, output=new_data, exclude_strings=exclude_strings)
        return type(self)(new_data)

    def align_nested(self, fieldsep: str = ",", linesep: str = "\n", tabsize: int = 4, tabs: bool = False) -> str:
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

        if not all([len(sublist) == len(self.data[0]) for sublist in self.data[1:]]):
            raise ValueError(f"All sublists must be the same length. The current breakdown is:\n\n{[len(sub) for sub in self]}\n\nThe sublists are:\n\n{self}")

        delimiter = "\t" if tabs else " "
        indices = range(len(self.data[0]))

        with_seps = [[text if index == (len(sublist) - 1) else f"{text}{fieldsep}" for index, text in enumerate(sublist)] for sublist in self.data]
        tab_sizes = {index: calculate_tabs_or_spaces_needed([sublist[index] for sublist in with_seps], with_tabs=tabs, tab_size=tabsize) for index in indices}
        adjusted = [[f"{with_seps[num][index]}{tab_sizes[index][num] * delimiter}" for index in indices] for num in range(len(with_seps))]

        return f"{linesep}".join(["".join(sublist).rstrip() for sublist in adjusted])

    def before(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ before the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)() if not matches else type(self)(self[:matches[0]])

    def before_first(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ before the first instance of the given value."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[:matches[0]])

    def before_last(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ before the last instance of the given value."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[:matches[-1]])

    def after(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ after the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)() if not matches else type(self)(self[matches[0]+1:])

    def after_first(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ after the first instance of the given value."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[matches[0]+1:])

    def after_last(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ after the last instance of the given value."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[matches[-1]+1:])

    def from_(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ from the given value onwards, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)() if not matches else type(self)(self[matches[0]:])

    def from_first(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ from the first instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[matches[0]:])

    def from_last(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ from the last instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[matches[-1]:])

    def until(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ until the given value, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)() if not matches else type(self)(self[:matches[0]+1])

    def until_first(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ until the first instance of the given value (including itself)."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[:matches[0]+1])

    def until_last(self, value: Any, raise_if_absent: bool = False) -> List_:
        """Return all elements (if any) in the List_ until the last instance of the given value (including itself)."""
        matches = self._slice_helper(value, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)() if not matches else type(self)(self[:matches[-1]+1])

    def _slice_helper(self, value: Any, raise_if_absent: bool = False, multiple_matches_forbidden: bool = False) -> List[int]:
        matches = [index for index, val in enumerate(self) if val == value]

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise ValueError(f"Too many matches, return value would be ambigous (Expected 1, got {len(matches)}).")

        if raise_if_absent and not matches:
            raise ValueError(f"'{value}' could not be found in '{self}'.")

        return matches
