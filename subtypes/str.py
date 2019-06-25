from __future__ import annotations

import collections
import itertools
import re as standard_re
from typing import Any, Callable, Iterator, List, Tuple, Match, Union, no_type_check
import warnings

import regex as re
import inflect
from lazy_property import LazyWritableProperty

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import fuzz


# TODO: Implement class-wide RegexSettings and FuzzyMatcher as well as instance-specific override functionality

class Str(collections.UserString, str):  # type: ignore
    regex = re

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.data: str
        super().__init__(*args, **kwargs)

    @no_type_check
    def __setitem__(self, key, item):
        aslist = list(self.data)
        aslist[key] = str(item)
        self.data = "".join(aslist)

    # stripping

    def strip_whitespace(self, leave_single_spaces: bool = True) -> Str:
        return self.sub(r"\s+", " " if leave_single_spaces else "").strip()

    def strip_non_alphanumeric(self) -> Str:
        return self.sub(r"[^A-Za-z0-9]", "")

    def strip_non_ascii(self) -> Str:
        return type(self)(self.data.encode("ascii", errors="ignore").decode("UTF-8"))

    # casing

    def camel_case(self, pascal: bool = True, preserve_upper: bool = True) -> Str:
        final = self.sub(r"[^A-Za-z0-9]+(.|$)", lambda m: m.group(1).upper())                                     # strip away any substrings of non-alphanumeric characters and uppercase whatever follows them
        if not preserve_upper:
            final = final.sub(r"([A-Z])([A-Z]+)(?=[A-Z][a-z]+)", lambda m: f"{m.group(1)}{m.group(2).lower()}")   # replace consecutive uppercase letters after the first with lowercase letters unless followed by lowercase letters
            final = final.sub(r"([A-Z])([A-Z]+)", lambda m: f"{m.group(1)}{m.group(2).lower()}")                  # replace consecutive uppercase letters after the first with lowercase letters
        final[0] = final[0].upper() if pascal else final[0].lower()                                               # capitalize the first word if pascal-casing else lower-case it
        return final

    def snake_case(self) -> Str:
        stage1 = re.sub(r"[^A-Za-z0-9]+", r"_", self.data)              # strip sequences of non-alphanumeric characters (including whitespace) and replace them with a single underscore
        stage2 = re.sub(r"([^A-Z_])([A-Z])", r"\1_\2", stage1)          # place an underscore at every boundary between a non-uppercase, non-underscore character and an uppercase character
        stage3 = re.sub(r"([A-Z]+)([A-Z])([a-z])", r"\1_\2\3", stage2)  # when finding multiple uppercase characters in a row place an underscore before the last one in the sequence if followed by a lowercase character
        final = re.sub(r"(_+)", r"_", stage3)                           # replace multiple underscores with a single underscore
        return type(self)(final.lower().strip("_"))                     # lowercase whatever is left and strip away trailing underscores

    def plural(self) -> Str:
        """Produce a 'pluralized' name, e.g. 'SomeTerm' -> 'SomeTerms'"""
        return type(self)(inflect.engine().plural(self.data))

    def identifier(self) -> Str:
        return type(self)(self.snake_case().sub(r"^(?=\d+)", "_"))

    # parsing

    def find_all(self, substring: str, regex: bool = False, overlapping: bool = True, not_within: List[Tuple[str, str]] = None) -> List[int]:
        pattern = substring if regex else re.escape(substring)
        prefix = "".join([fr"{start}.*?{end}|" for start, end in not_within]) if not_within is not None else ""
        return [match.start() for match in re.finditer(fr"{prefix}({pattern})", self.data, overlapped=overlapping if not_within is None else False, flags=self.re() if regex else 0) if match.group(1)]

    def extract_uk_postcode(self) -> Str:
        match = re.search(r"([A-Za-z]{1,2}[0-9]{1,2}[A-Za-z]?)( )?([0-9][A-Za-z]{2})", self.data)
        return type(self)(f"{match.group(1).upper()} {match.group(3).upper()}")

    # regex

    def configure_re(self, dotall: bool = True, ignorecase: bool = True, multiline: bool = False) -> Str:
        self.re = RegexSettings(dotall=dotall, ignorecase=ignorecase, multiline=multiline)
        return self

    def search(self, regex: str, **kwargs: Any) -> Match[str]:
        return re.search(regex, self.data, flags=self.re(), **kwargs)

    def sub(self, regex: str, sub: Union[str, Callable], raise_for_failure: bool = False, **kwargs: Any) -> Str:
        subbed = re.sub(regex, sub, self.data, flags=self.re(), **kwargs)

        if raise_for_failure:
            if self.data == subbed:
                raise RuntimeError(f"'{self.data}' was not changed!")

        return type(self)(subbed)

    def finditer(self, regex: str, **kwargs: Any) -> Iterator[Match[str]]:
        return re.finditer(regex, self.data, flags=self.re(), **kwargs)

    def splitre(self, regex: str, **kwargs: Any) -> List[Str]:
        return [type(self)(item) for item in re.split(regex, self.data, flags=self.re(), **kwargs)]

    def before(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)("") if not matches else type(self)(self.data[:matches[0].span()[0]])

    def before_first(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)("") if not matches else type(self)(self.data[:matches[0].span()[0]])

    def before_last(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)("") if not matches else type(self)(self.data[:matches[-1].span()[0]])

    def after(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=True)
        return type(self)("") if not matches else type(self)(self.data[matches[0].span()[1]:])

    def after_first(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)("") if not matches else type(self)(self.data[matches[0].span()[1]:])

    def after_last(self, regex: str, raise_if_absent: bool = False) -> Str:
        matches = self._before_after_helper(regex, raise_if_absent=raise_if_absent, multiple_matches_forbidden=False)
        return type(self)("") if not matches else type(self)(self.data[matches[-1].span()[1]:])

    def _before_after_helper(self, regex: str, raise_if_absent: bool = False, multiple_matches_forbidden: bool = False) -> List[Match[str]]:
        matches = list(self.finditer(regex=regex))

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise RuntimeError(f"Too many matches, return value would be ambigous (Expected 1, got {len(matches)}). Use one of: {', '.join([f'{type(self).__name__}.{method}()' for method in ('before_first', 'before_last', 'after_first', 'after_last')])}")

        if raise_if_absent and not matches:
            raise RuntimeError(f"'{regex}' could not be found in '{self}'.")

        return matches

    # fuzzy matching

    def configure_fuzzy(self, tokenize: bool = False, partial: bool = False) -> Str:
        self.fuzzy = FuzzyMatcher(tokenize=tokenize, partial=partial)
        return self

    def fuzzy_match(self, other: str) -> int:
        return self.fuzzy.match(self.data, other)

    def best_n_fuzzy_matches(self, possible_matches: List[str], num: int = 3) -> List[Tuple[str, int]]:
        match_scores = {self.fuzzy_match(match): match for match in possible_matches}
        return [(match_scores[score], score) for index, score in itertools.takewhile(lambda tup: tup[0] < num, enumerate(sorted(match_scores, reverse=True)))]

    @LazyWritableProperty
    def fuzzy(self) -> FuzzyMatcher:
        return FuzzyMatcher()

    @LazyWritableProperty
    def re(self) -> RegexSettings:
        return RegexSettings()


class RegexSettings:
    def __init__(self, dotall: bool = True, ignorecase: bool = True, multiline: bool = False):
        self.dotall, self.ignorecase, self.multiline = dotall, ignorecase, multiline

    def __and__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.get_flag() & other

    def __or__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.get_flag() | other

    def __rand__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.get_flag() & other

    def __ror__(self, other: Union[int, re.RegexFlag]) -> int:
        return self.get_flag() | other

    def __call__(self) -> re.RegexFlag:
        return self.get_flag()

    def get_flag(self) -> re.RegexFlag:
        ret = standard_re.RegexFlag(0)
        for attr, flag in (self.dotall, re.DOTALL), (self.ignorecase, re.IGNORECASE), (self.multiline, re.MULTILINE):
            if attr:
                ret |= flag
        return ret


class FuzzyMatcher:
    def __init__(self, tokenize: bool = False, partial: bool = False) -> None:
        self._tokenize, self._partial, self._ready = tokenize, partial, False
        self._prepare()

    def __repr__(self) -> str:
        return f"{type(self).__name__}({', '.join([f'{attr}={repr(val)}' for attr, val in self.__dict__.items() if not attr.startswith('_')])})"

    def __call__(self, first: str, second: str) -> int:
        return self.match(first=first, second=second)

    @property
    def tokenize(self) -> bool:
        return self._tokenize

    @tokenize.setter
    def tokenize(self, val: bool) -> None:
        self._tokenize, self._ready = val, False

    @property
    def partial(self) -> bool:
        return self._tokenize

    @partial.setter
    def partial(self, val: bool) -> None:
        self._partial, self._ready = val, False

    def match(self, first: str, second: str) -> int:
        if not self._ready:
            self._prepare()
        return self._matcher(first, second)

    def _prepare(self) -> None:
        for func, tokenize, partial in [(fuzz.ratio, False, False), (fuzz.partial_ratio, False, True), (fuzz.token_set_ratio, True, False), (fuzz.partial_token_set_ratio, True, True)]:
            if self.tokenize is tokenize and self.partial is partial:
                self._matcher, self._ready = func, True
                return
