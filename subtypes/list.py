from __future__ import annotations

import collections
from typing import Any, Dict, Iterable, List, Tuple, no_type_check

from lazy_property import LazyProperty

from .str import FuzzyMatcher


class List_(collections.UserList, list):  # type: ignore
    data: list

    @LazyProperty
    def fuzzy(self) -> FuzzyMatcher:
        return FuzzyMatcher()

    @no_type_check
    def append(self, item):
        self.data.append(item)
        return self

    @no_type_check
    def extend(self, item):
        self.data.extend(item)
        return self

    @no_type_check
    def insert(self, index, item):
        self.data.insert(index, item)
        return self

    @no_type_check
    def remove(self, item):
        self.data.remove(item)
        return self

    @no_type_check
    def reverse(self):
        self.data.reverse()
        return self

    @no_type_check
    def sort(self):
        self.data.sort()
        return self

    @no_type_check
    def clear(self):
        self.data.clear()
        return self

    def flatten(self, exclude_strings: bool = True) -> List_:
        def recurse(iterable: Iterable, output: list, exclude_strings: bool) -> None:
            for item in iterable:
                if hasattr(item, "__iter__") and (not isinstance(item, str) or not exclude_strings):
                    recurse(iterable=item, output=output, exclude_strings=exclude_strings)
                else:
                    output.append(item)

        new_data: list = []
        recurse(iterable=self.data, output=new_data, exclude_strings=exclude_strings)
        self.data = new_data
        return self

    def fuzzy_match_lists(self, other: List[Any], match_cutoff: int = 100) -> List[Tuple[Any, Any]]:
        fuzzy_matches = []
        for str1 in self.data:
            for str2 in other:
                if self.fuzzy(str1, str2) >= match_cutoff:
                    fuzzy_matches.append((str1, str2))
        return fuzzy_matches

    def align_nested(self, fieldsep: str = ",", linesep: str = "\n", tabsize: int = 4, tabs: bool = False) -> str:
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
