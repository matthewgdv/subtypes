from __future__ import annotations

import collections
import copy
import itertools
import re
from typing import Any, Callable, Iterator, List, Tuple, Dict, Match, Union, no_type_check
import warnings

import regex as regexmod
import case_conversion
import inflect
import clipboard

from maybe import Maybe

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import fuzz


class RegexSettings:
    def __init__(self, dotall: bool = True, ignorecase: bool = True, multiline: bool = False):
        self.dotall, self.ignorecase, self.multiline = dotall, ignorecase, multiline

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"

    def __int__(self) -> int:
        return self.to_flag()

    def __and__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.to_flag() & other

    def __or__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.to_flag() | other

    def __rand__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.to_flag() & other

    def __ror__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.to_flag() | other

    def __call__(self, dotall: bool = None, ignorecase: bool = None, multiline: bool = None) -> RegexSettings:
        self.dotall, self.ignorecase, self.multiline = Maybe(dotall).else_(self.dotall), Maybe(ignorecase).else_(self.ignorecase), Maybe(multiline).else_(self.multiline)
        return self

    def to_flag(self) -> re.RegexFlag:
        ret = re.RegexFlag(0)
        for attr, flag in (self.dotall, re.DOTALL), (self.ignorecase, re.IGNORECASE), (self.multiline, re.MULTILINE):
            if attr:
                ret |= flag
        return ret


class RegexAccessor:
    """An accessor class for all regex-related Str methods"""
    settings = RegexSettings()

    def __init__(self, parent: Str = None, settings: RegexSettings = None) -> None:
        default = type(self).settings
        self.parent, self.settings = parent, RegexSettings(dotall=default.dotall, ignorecase=default.ignorecase, multiline=default.multiline) if settings is None else settings

    def __call__(self, parent: Str = None, settings: RegexSettings = None) -> RegexAccessor:
        self.parent, self.settings = Maybe(parent).else_(self.parent), Maybe(settings).else_(self.settings)
        return self

    def search(self, regex: str, **kwargs: Any) -> Match[str]:
        """Perform a regex.search on this Str"""
        ret: Match[str] = regexmod.search(regex, self.parent, flags=Maybe(kwargs.pop("flags", None)).else_(self.settings.to_flag()), **kwargs)
        return ret

    def sub(self, regex: str, sub: Union[str, Callable], raise_for_failure: bool = False, **kwargs: Any) -> Str:
        """Perform a regex.search on this Str"""
        subbed = regexmod.sub(regex, sub, self.parent, flags=Maybe(kwargs.pop("flags", None)).else_(self.settings.to_flag()), **kwargs)

        if raise_for_failure:
            if self.parent == subbed:
                raise ValueError(f"'{self.parent}' was not changed!")

        return type(self.parent)(subbed)

    def finditer(self, regex: str, **kwargs: Any) -> Iterator[Match[str]]:
        """Perform a regex.finditer on this Str"""
        ret: Iterator[Match[str]] = regexmod.finditer(regex, self.parent, flags=Maybe(kwargs.pop("flags", None)).else_(self.settings.to_flag()), **kwargs)
        return ret

    def split(self, regex: str, **kwargs: Any) -> List[Str]:
        """Perform a regex.split on this Str"""
        return [type(self.parent)(item) for item in regexmod.split(regex, self.parent, flags=Maybe(kwargs.pop("flags", None)).else_(self.settings.to_flag()), **kwargs)]

    def escape(self) -> str:
        """Perform a re.escape on this Str"""
        return type(self.parent)(re.escape(self.parent))


class FuzzyAccessor:
    """An accessor class for all fuzzy-matching-related Str methods"""

    def __init__(self, parent: Str = None, tokenize: bool = False, partial: bool = False) -> None:
        self.parent, self.tokenize, self.partial = parent, tokenize, partial
        self._determine_matcher()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"

    def __call__(self, parent: Str = None, tokenize: bool = None, partial: bool = None) -> FuzzyAccessor:
        self.parent, self.tokenize, self.partial = Maybe(parent).else_(self.parent), Maybe(tokenize).else_(self.tokenize), Maybe(partial).else_(self.partial)
        self._determine_matcher()
        return self

    def match(self, other: str) -> int:
        """Return a score out of 100 representing a fuzzy-match between this Str and another using the current fuzzy-matching settings"""
        return self._match(self.parent, other)

    def best_n_matches(self, possible_matches: List[str], num: int = 3) -> Dict[str, int]:
        """Return a number of the best fuzzy matches between this Str and an iterable of strings in descending order using the current fuzzy-matching settings"""
        match_scores = {self.match(match): match for match in possible_matches}
        return {match_scores[score]: score for index, score in itertools.takewhile(lambda tup: tup[0] < num, enumerate(sorted(match_scores, reverse=True)))}

    def _match(self, first: str, second: str) -> int:
        return self._matcher(first, second)

    def _determine_matcher(self) -> None:
        for func, tokenize, partial in [(fuzz.ratio, False, False), (fuzz.partial_ratio, False, True), (fuzz.token_set_ratio, True, False), (fuzz.partial_token_set_ratio, True, True)]:
            if self.tokenize is tokenize and self.partial is partial:
                self._matcher, self._ready = func, True
                return


class CasingAccessor:
    """An accessor class for all casing-related Str methods"""

    def __init__(self, parent: Str = None, detect_acronyms: bool = True, acronyms: list = None) -> None:
        self.parent, self.detect, self.acronyms = parent, detect_acronyms, Maybe(acronyms).else_([])

    def __call__(self, parent: Str = None, detect_acronyms: bool = None, acronyms: list = None) -> CasingAccessor:
        self.parent, self.detect, self.acronyms = Maybe(parent).else_(self.parent), Maybe(detect_acronyms).else_(self.detect), Maybe(acronyms).else_(self.acronyms)
        return self

    def snake(self) -> Str:
        """snake_case this Str"""
        return type(self.parent)(case_conversion.snakecase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms).strip("_"))

    def camel(self) -> Str:
        """camelCase this Str"""
        return type(self.parent)(case_conversion.camelcase(self.snake(), detect_acronyms=self.detect, acronyms=self.acronyms))

    def pascal(self) -> Str:
        """PascalCase this Str"""
        return type(self.parent)(case_conversion.pascalcase(self.snake(), detect_acronyms=self.detect, acronyms=self.acronyms))

    def dash(self) -> Str:
        """dash-case this Str"""
        return type(self.parent)(case_conversion.dashcase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms))

    def constant(self) -> Str:
        """CONSTANT_CASE this Str"""
        return type(self.parent)(case_conversion.constcase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms))

    def dot(self) -> Str:
        """dot.case this Str"""
        return type(self.parent)(case_conversion.dotcase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms))

    def slash(self) -> Str:
        """slash/case this Str"""
        return type(self.parent)(case_conversion.slashcase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms))

    def backslash(self) -> Str:
        """backslash\\case this Str"""
        return type(self.parent)(case_conversion.backslashcase(self.parent, detect_acronyms=self.detect, acronyms=self.acronyms))

    def identifier(self) -> Str:
        """Turn this Str into a valid python identifier"""
        return self.snake().re.sub(r"^(?=\d+)", "_")

    def plural(self) -> Str:
        """Return the plural of this Str"""
        return type(self.parent)(inflect.engine().plural(self.parent))


class SliceAccessor:
    """An accessor class for all slicing-related Str methods"""

    def __init__(self, parent: Str = None, raise_if_absent: bool = False) -> None:
        self.parent, self.raise_if_absent = parent, raise_if_absent

    def __call__(self, parent: Str = None, raise_if_absent: bool = None) -> SliceAccessor:
        self.parent, self.raise_if_absent = Maybe(parent).else_(self.parent), Maybe(raise_if_absent).else_(self.raise_if_absent)
        return self

    def before(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str before the given regex. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[0]])

    def before_first(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str before the first instance of the given regex."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[0]])

    def before_last(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str before the last instance of the given regex."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[-1].span()[0]])

    def after(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str after the given regex. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[1]:])

    def after_first(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str after the first instance of the given regex."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[1]:])

    def after_last(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str after the last instance of the given regex."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[-1].span()[1]:])

    def from_(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str from the given regex onwards (including itself). Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[0]:])

    def from_first(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str from the first instance of the given regex onwards (including itself)."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[0]:])

    def from_last(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str from the last instance of the given regex onwards (including itself)."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[-1].span()[0]:])

    def until(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str until given regex (including itself). Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[1]])

    def until_first(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str until the first instance of the given regex (including itself)."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[1]])

    def until_last(self, regex: str, raise_if_absent: bool = None) -> Str:
        """Return a new Str from the portion of this Str until the last instance of the given regex (including itself)."""
        matches = self._slice_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[-1].span()[1]])

    def _slice_helper(self, regex: str, raise_if_absent: bool, multiple_matches_forbidden: bool) -> List[Match[str]]:
        matches = list(self.parent.re.finditer(regex=regex))

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise ValueError(f"Too many matches, return value would be ambigous (Expected 1, got {len(matches)}).")

        if Maybe(raise_if_absent).else_(self.raise_if_absent) and not matches:
            raise ValueError(f"'{regex}' could not be found in '{self}'.")

        return matches


class StripAccessor:
    """An accessor class for all stripping-related Str methods"""

    def __init__(self, parent: Str = None) -> None:
        self.parent = parent

    def __call__(self, parent: Str = None) -> StripAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        return self

    def all_whitespace(self) -> Str:
        """Strip away all whitespace"""
        return self.parent.re.sub(r"\s+", "").strip()

    def whitespace_runs(self) -> Str:
        """Replace all whitespace runs with a single space"""
        return self.parent.re.sub(r"\s*\n\s*", "\n").re.sub(r"[ \t]*\t[ \t]*", "\t").re.sub(r"( )+", " ").strip()

    def non_alphanumeric(self) -> Str:
        """Strip away all non-alphanumeric characters"""
        return self.parent.re.sub(r"[^A-Za-z0-9]", "")

    def non_ascii(self) -> Str:
        """Strip away all non-ascii characters"""
        return type(self.parent)(self.parent.encode("ascii", errors="ignore").decode("UTF-8"))


class Str(collections.UserString, str):  # type: ignore
    """A subclass of the builin 'str' class which supports inplace mutation using item access. Has additional methods and accessor objects with additional methods for casing, regex, fuzzy-matching, stripping, and slicing."""
    re, case, slice, strip_, fuzzy = RegexAccessor(), CasingAccessor(), SliceAccessor(), StripAccessor(), FuzzyAccessor()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data: str
        cls = type(self)

        self.re = RegexAccessor(parent=self)
        self.case = CasingAccessor(parent=self, detect_acronyms=cls.case.detect_acronyms, acronyms=cls.case.acronyms)
        self.slice = SliceAccessor(parent=self, raise_if_absent=cls.slice.raise_if_absent)
        self.strip_ = StripAccessor(parent=self)
        self.fuzzy = FuzzyAccessor(parent=self, tokenize=cls.fuzzy.tokenize, partial=cls.fuzzy.partial)

    @no_type_check
    def __setitem__(self, key, item):
        aslist = list(self.data)
        aslist[key] = str(item)
        self.data = "".join(aslist)

    def to_clipboard(self) -> None:
        """Safe the contents of this string to the clipboard"""
        clipboard.copy(self.data)

    # parsing

    def find_all(self, substring: str, regex: bool = False, overlapping: bool = True, not_within: List[Tuple[str, str]] = None) -> List[int]:
        """Return a list of all the index positions at which the given substring occurs."""
        pattern = substring if regex else re.escape(substring)
        prefix = "".join([fr"{start}.*?{end}|" for start, end in not_within]) if not_within is not None else ""
        return [match.start() for match in regexmod.finditer(fr"{prefix}({pattern})", self.data, overlapped=overlapping if not_within is None else False, flags=self.re.settings.to_flag() if regex else 0) if match.group(1)]

    def extract_uk_postcode(self) -> Str:
        """Attempt to extract a valid UK postcode from the given string. Returns None upon failure."""
        match = self.re.search(r"([A-Za-z]{1,2}[0-9]{1,2}[A-Za-z]?)( )?([0-9][A-Za-z]{2})")
        return None if match is None else type(self)(f"{match.group(1).upper()} {match.group(3).upper()}")

    @classmethod
    def from_clipboard(cls) -> Str:
        """Create a Str from the contents of the clipboard"""
        return cls(clipboard.paste())
