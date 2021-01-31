from __future__ import annotations

import copy
import itertools
from functools import reduce
from operator import ior
import re
from typing import Any, Callable, Iterator, Iterable, Tuple, Mapping, Match, Union
import warnings

import regex as regexmod
import case_conversion
import inflect
import clipboard
from .lazy import cached_property

from maybe import Maybe

from .enums import Enum
from .translator import TranslatableMeta

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import fuzz


class Accessor:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"


class Settings:
    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"

    def deepcopy(self) -> Settings:
        return copy.deepcopy(self)


class RegexAccessor(Accessor):
    """An accessor class for all regex-related Str methods"""

    class Settings(Settings):
        dotall, ignorecase, multiline = True, True, False

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

        def to_flag(self) -> int:
            flags = [flag for attr, flag in [(self.dotall, re.DOTALL), (self.ignorecase, re.IGNORECASE), (self.multiline, re.MULTILINE)]]
            return reduce(ior, flags)

    def __init__(self, parent: Str = None) -> None:
        self.parent, self.settings = parent, self.Settings()

    def __call__(self, parent: Str = None, dotall: bool = None, ignorecase: bool = None, multiline: bool = None) -> RegexAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        self.settings.dotall = Maybe(dotall).else_(self.settings.dotall)
        self.settings.ignorecase = Maybe(ignorecase).else_(self.settings.ignorecase)
        self.settings.multiline = Maybe(multiline).else_(self.settings.multiline)
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

    def split(self, regex: str, **kwargs: Any) -> list[Str]:
        """Perform a regex.split on this Str"""
        return [type(self.parent)(item) for item in regexmod.split(regex, self.parent, flags=Maybe(kwargs.pop("flags", None)).else_(self.settings.to_flag()), **kwargs)]

    def escape(self) -> str:
        """Perform a re.escape on this Str"""
        return type(self.parent)(re.escape(self.parent))


class FuzzyAccessor(Accessor):
    """An accessor class for all fuzzy-matching-related Str methods"""

    class Settings(Settings):
        tokenize, partial = False, False

    def __init__(self, parent: Str = None) -> None:
        self.parent, self.settings = parent, self.Settings()
        self._determine_matcher()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"

    def __call__(self, parent: Str = None, tokenize: bool = None, partial: bool = None) -> FuzzyAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        self.settings.tokenize = Maybe(tokenize).else_(self.settings.tokenize)
        self.settings.partial = Maybe(partial).else_(self.settings.partial)
        self._determine_matcher()
        return self

    def match(self, other: str) -> int:
        """Return a score out of 100 representing a fuzzy-match between this Str and another using the current fuzzy-matching settings"""
        return self._matcher(self.parent, other)

    def best_n_matches(self, possible_matches: list[str], num: int = 3) -> dict[str, int]:
        """Return a number of the best fuzzy matches between this Str and an iterable of strings in descending order using the current fuzzy-matching settings"""
        match_scores = {self.match(match): match for match in possible_matches}
        return {match_scores[score]: score for index, score in itertools.takewhile(lambda tup: tup[0] < num, enumerate(sorted(match_scores, reverse=True)))}

    def _determine_matcher(self) -> None:
        for func, tokenize, partial in [(fuzz.ratio, False, False), (fuzz.partial_ratio, False, True), (fuzz.token_set_ratio, True, False), (fuzz.partial_token_set_ratio, True, True)]:
            if self.settings.tokenize is tokenize and self.settings.partial is partial:
                self._matcher = func
                return


class CasingAccessor(Accessor):
    """An accessor class for all casing-related Str methods"""

    def __init__(self, parent: Str = None) -> None:
        self.parent = parent

    def __call__(self, parent: Str = None, acronyms: list = None) -> CasingAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        return self

    def snake(self) -> Str:
        """snake_case this Str"""
        return type(self.parent)(case_conversion.snakecase(self.parent).strip("_"))

    def camel(self) -> Str:
        """camelCase this Str"""
        return type(self.parent)(case_conversion.camelcase(self.snake()))

    def pascal(self) -> Str:
        """PascalCase this Str"""
        return type(self.parent)(case_conversion.pascalcase(self.snake()))

    def dash(self) -> Str:
        """dash-case this Str"""
        return type(self.parent)(case_conversion.dashcase(self.parent))

    def constant(self) -> Str:
        """CONSTANT_CASE this Str"""
        return type(self.parent)(case_conversion.constcase(self.parent))

    def dot(self) -> Str:
        """dot.case this Str"""
        return type(self.parent)(case_conversion.dotcase(self.parent))

    def slash(self) -> Str:
        """slash/case this Str"""
        return type(self.parent)(case_conversion.slashcase(self.parent))

    def backslash(self) -> Str:
        """backslash\\case this Str"""
        return type(self.parent)(case_conversion.backslashcase(self.parent))

    def identifier(self) -> Str:
        """Turn this Str into a valid python identifier by first snake_casing it and then stripping away invalid characters"""
        return self.snake().re.sub(r"^(?=\d+)", "_")

    def plural(self) -> Str:
        """Return the English plural of this Str"""
        return type(self.parent)(inflect.engine().plural(self.parent))

    def from_enum(self, case: Str.Case) -> Str:
        return getattr(self, str(case))()


class SliceAccessor(Accessor):
    """An accessor class for all slicing-related Str methods"""

    class Settings(Settings):
        raise_if_absent = False

    def __init__(self, parent: Str = None) -> None:
        self.parent, self.settings = parent, self.Settings()

    def __call__(self, parent: Str = None, raise_if_absent: bool = None) -> SliceAccessor:
        self.parent, self.settings.raise_if_absent = Maybe(parent).else_(self.parent), Maybe(raise_if_absent).else_(self.settings.raise_if_absent)
        return self

    def before(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str before the given regex. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[0]])

    def before_first(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str before the first instance of the given regex."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[0]])

    def before_last(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str before the last instance of the given regex."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[-1].span()[0]])

    def after(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str after the given regex. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[1]:])

    def after_first(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str after the first instance of the given regex."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[1]:])

    def after_last(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str after the last instance of the given regex."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[-1].span()[1]:])

    def from_(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str from the given regex onwards (including itself). Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[0]:])

    def from_first(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str from the first instance of the given regex onwards (including itself)."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[0].span()[0]:])

    def from_last(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str from the last instance of the given regex onwards (including itself)."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[matches[-1].span()[0]:])

    def until(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str until given regex (including itself). Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=True)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[1]])

    def until_first(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str until the first instance of the given regex (including itself)."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[0].span()[1]])

    def until_last(self, regex: str) -> Str:
        """Return a new Str from the portion of this Str until the last instance of the given regex (including itself)."""
        matches = self._slice_helper(regex, multiple_matches_forbidden=False)
        return type(self.parent)("") if not matches else type(self.parent)(self.parent[:matches[-1].span()[1]])

    def _slice_helper(self, regex: str, multiple_matches_forbidden: bool) -> list[Match[str]]:
        matches = list(self.parent.re.finditer(regex=regex))

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise ValueError(f"Too many matches for regex pattern '{regex}' in '{self.parent}', return value would be ambigous (Expected 1, got {len(matches)}).")

        if self.settings.raise_if_absent and not matches:
            raise ValueError(f"'{regex}' could not be found in '{self.parent}'.")

        return matches


class TrimAccessor(Accessor):
    """An accessor class for all stripping-related Str methods"""

    def __init__(self, parent: Str = None) -> None:
        self.parent = parent

    def __call__(self, parent: Str = None) -> TrimAccessor:
        self.parent = Maybe(parent).else_(self.parent)
        return self

    def all_whitespace(self) -> Str:
        """Strip away all whitespace"""
        return self.parent.re.sub(r"\s+", "").strip()

    def whitespace_runs(self, newlines: int = 1, tabs: int = 1, spaces: int = 1) -> Str:
        """Replace all whitespace runs with a single instance of the appropriate whitespace character space"""
        return self.parent.re.sub(r"[ \t]*\n[ \t]*", "\n").re.sub(r" *\t *", "\t").re.sub(fr"\n{{{newlines+1},}}", "\n"*newlines).re.sub(fr"\t{{{tabs+1},}}", "\t"*tabs).re.sub(fr" {{{spaces+1},}}", " "*spaces).strip()

    def non_alphanumeric(self) -> Str:
        """Strip away all non-alphanumeric characters"""
        return self.parent.re.sub(r"[^A-Za-z0-9]", "")

    def non_ascii(self) -> Str:
        """Strip away all non-ascii characters"""
        return type(self.parent)(self.parent.encode("ascii", errors="ignore").decode("UTF-8"))


class BaseStr(str):
    """An alternative implementation of collections.UserString that inherits directly from 'str'."""

    def __add__(self, other: str) -> BaseStr:
        return type(self)(super().__add__(other))

    def __radd__(self, other: str) -> BaseStr:
        return type(self)(other) + self

    def __mul__(self, n) -> BaseStr:
        return type(self)(super().__mul__(n))

    def __rmul__(self, n) -> BaseStr:
        return self*n

    def __mod__(self, args: Any) -> BaseStr:
        return type(self)(super().__mod__(args))

    def __rmod__(self, template: str) -> BaseStr:
        return type(self)(template) % self

    def capitalize(self) -> BaseStr:
        return type(self)(super().capitalize())

    def casefold(self) -> BaseStr:
        return type(self)(super().casefold())

    def center(self, width, *args) -> BaseStr:
        return type(self)(super().center(width, *args))

    def expandtabs(self, tabsize: int = 8) -> BaseStr:
        return type(self)(super().expandtabs(tabsize))

    def format(self, *args: Any, **kwds: Any) -> BaseStr:
        return type(self)(super().format(*args, **kwds))

    def format_map(self, mapping: Mapping[str, Any]) -> BaseStr:
        return type(self)(super().format_map(mapping))

    def join(self, iterable: Iterable[str]) -> BaseStr:
        return type(self)(super().join(iterable))

    def ljust(self, width: int, fillchar: str = " ") -> BaseStr:
        return type(self)(super().ljust(width, fillchar))

    def lower(self) -> BaseStr:
        return type(self)(super().lower())

    def lstrip(self, chars: str = None) -> BaseStr:
        return type(self)(super().lstrip(chars))

    def partition(self, sep: str) -> Tuple[BaseStr, ...]:
        return tuple(type(self)(item) for item in super().partition(sep))

    def replace(self, old: str, new: str, maxsplit: int = -1) -> BaseStr:
        return type(self)(super().replace(old, new, maxsplit))

    def rjust(self, width: int, fillchar: str = " ") -> BaseStr:
        return type(self)(super().rjust(width, fillchar))

    def rpartition(self, sep: str) -> Tuple[BaseStr, ...]:
        return tuple(type(self)(item) for item in super().rpartition(sep))

    def rstrip(self, chars: str = None) -> BaseStr:
        return type(self)(super().rstrip(chars))

    def strip(self, chars: str = None) -> BaseStr:
        return type(self)(super().strip(chars))

    def swapcase(self) -> BaseStr:
        return type(self)(super().swapcase())

    def title(self) -> BaseStr:
        return type(self)(super().title())

    def translate(self, *args) -> BaseStr:
        return type(self)(super().translate(*args))

    def upper(self) -> BaseStr:
        return type(self)(super().upper())

    def zfill(self, width: int) -> BaseStr:
        return type(self)(super().zfill(width))


class Str(BaseStr, metaclass=TranslatableMeta):
    """A subclass of the builin 'str' class which supports inplace mutation using item access. Has additional methods and accessor objects with additional methods for casing, regex, fuzzy-matching, trimming, and slicing."""

    class Case(Enum):
        SNAKE, CAMEL, PASCAL, CONSTANT = CasingAccessor.snake.__name__, CasingAccessor.camel.__name__, CasingAccessor.pascal.__name__, CasingAccessor.constant.__name__
        DOT, DASH, SLASH, BACKSLASH = CasingAccessor.dot.__name__, CasingAccessor.dash.__name__, CasingAccessor.slash.__name__, CasingAccessor.backslash.__name__
        IDENTIFIER, PLURAL = CasingAccessor.identifier.__name__, CasingAccessor.plural.__name__

    class Accessors(Settings):
        re, case, slice, trim, fuzzy = RegexAccessor, CasingAccessor, SliceAccessor, TrimAccessor, FuzzyAccessor

    @cached_property
    def re(self) -> RegexAccessor:
        return self.Accessors.re(parent=self)

    @cached_property
    def case(self) -> CasingAccessor:
        return self.Accessors.case(parent=self)

    @cached_property
    def slice(self) -> SliceAccessor:
        return self.Accessors.slice(parent=self)

    @cached_property
    def trim(self) -> TrimAccessor:
        return self.Accessors.trim(parent=self)

    @cached_property
    def fuzzy(self) -> FuzzyAccessor:
        return self.Accessors.fuzzy(parent=self)

    def to_clipboard(self) -> None:
        """Save the content of this string to the clipboard"""
        clipboard.copy(self)

    # parsing

    def find_all(self, substring: str, regex: bool = False, overlapping: bool = True, not_within: list[Tuple[str, str]] = None) -> list[int]:
        """Return a list of all the index positions at which the given substring occurs."""
        pattern = substring if regex else re.escape(substring)
        prefix = "".join([fr"{start}.*?{end}|" for start, end in not_within]) if not_within is not None else ""
        return [match.start() for match in regexmod.finditer(fr"{prefix}({pattern})", self, overlapped=overlapping if not_within is None else False, flags=self.re.settings.to_flag() if regex else 0) if match.group(1)]

    def extract_uk_postcode(self) -> Str:
        """Attempt to extract a valid UK postcode from the given string. Returns None upon failure."""
        match = self.re.search(r"([A-Za-z]{1,2}[0-9]{1,2}[A-Za-z]?)( )?([0-9][A-Za-z]{2})")
        return None if match is None else type(self)(f"{match.group(1).upper()} {match.group(3).upper()}")

    @classmethod
    def from_clipboard(cls) -> Str:
        """Create a Str from the content of the clipboard"""
        return cls(clipboard.paste())
