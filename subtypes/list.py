from __future__ import annotations

from collections.abc import Sequence
import json
from typing import Any, Iterable, Iterator, Callable, Union

from .lazy import cached_property

from maybe import Maybe

from .str import Accessor, Settings
from .translator import TranslatableMeta


class SliceAccessor(Accessor):
    """An accessor class for all slicing-related Str methods"""

    class Settings(Settings):
        raise_if_absent = False

    def __init__(self, parent: List = None) -> None:
        self.parent, self.settings = parent, self.Settings()

    def __call__(self, parent: List = None, raise_if_absent: bool = None) -> SliceAccessor:
        self.parent, self.settings.raise_if_absent = Maybe(parent).else_(self.parent), Maybe(raise_if_absent).else_(self.settings.raise_if_absent)
        return self

    def before(self, value: Any) -> List:
        """Return all elements (if any) in the List before the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]])

    def before_first(self, value: Any) -> List:
        """Return all elements (if any) in the List before the first instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]])

    def before_last(self, value: Any) -> List:
        """Return all elements (if any) in the List before the last instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[-1]])

    def after(self, value: Any) -> List:
        """Return all elements (if any) in the List after the given value. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]+1:])

    def after_first(self, value: Any) -> List:
        """Return all elements (if any) in the List after the first instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]+1:])

    def after_last(self, value: Any) -> List:
        """Return all elements (if any) in the List after the last instance of the given value."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[-1]+1:])

    def from_(self, value: Any) -> List:
        """Return all elements (if any) in the List from the given value onwards, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]:])

    def from_first(self, value: Any) -> List:
        """Return all elements (if any) in the List from the first instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[0]:])

    def from_last(self, value: Any) -> List:
        """Return all elements (if any) in the List from the last instance of the given value onwards (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[matches[-1]:])

    def until(self, value: Any) -> List:
        """Return all elements (if any) in the List until the given value, including itself. Raises ValueError if multiple matches are found."""
        matches = self._slice_helper(value, multiple_matches_forbidden=True)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]+1])

    def until_first(self, value: Any) -> List:
        """Return all elements (if any) in the List until the first instance of the given value (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[0]+1])

    def until_last(self, value: Any) -> List:
        """Return all elements (if any) in the List until the last instance of the given value (including itself)."""
        matches = self._slice_helper(value, multiple_matches_forbidden=False)
        return type(self.parent)() if not matches else type(self.parent)(self.parent[:matches[-1]+1])

    def _slice_helper(self, value: Any, multiple_matches_forbidden: bool) -> list[int]:
        matches = [index for index, val in enumerate(self.parent) if val == value]

        if multiple_matches_forbidden:
            if len(matches) > 1:
                raise ValueError(f"Too many matches, return value would be ambigous (Expected 1, got {len(matches)}).")

        if self.settings.raise_if_absent and not matches:
            raise ValueError(f"'{value}' could not be found in '{self.parent}'.")

        return matches


class AttributeAccessor(Accessor):
    def __init__(self, parent: List) -> None:
        self.parent = parent

    def __getattr__(self, attr: str) -> List:
        return type(self.parent)([getattr(item, attr) for item in self.parent])


# noinspection PyArgumentList
class BaseList(list):
    """
    An alternative implementation of collections.UserList that inherits directly from 'list'. All the 'list' class inplace methods return self and therefore allow chaining when called from this class.
    """

    def __getitem__(self, item: Union[slice, int]) -> Union[BaseList, Any]:
        return type(self)(ret) if isinstance((ret := list(self)[item]), list) else ret

    def __add__(self, other: list) -> BaseList:
        return type(self)(super().__add__(other))

    def __radd__(self, other: list) -> BaseList:
        return type(self)(other.__add__(self))

    def __iadd__(self, other):
        super().__iadd__(other)
        return self

    def __mul__(self, n: int) -> BaseList:
        return type(self)(super().__mul__(n))

    def __rmul__(self, n: int) -> BaseList:
        return type(self)(super().__rmul__(n))

    def __imul__(self, n: int) -> BaseList:
        super().__imul__(n)
        return self

    def append(self, item: Any) -> BaseList:
        """Same as list.append(), but returns self and thus allows chaining."""
        super().append(item)
        return self

    def extend(self, item: Any) -> BaseList:
        """Same as list.extend(), but returns self and thus allows chaining."""
        super().extend(item)
        return self

    def insert(self, index: int, item: Any) -> BaseList:
        """Same as list.insert(), but returns self and thus allows chaining."""
        super().insert(index, item)
        return self

    def remove(self, item: Any) -> BaseList:
        """Same as list.remove(), but returns self and thus allows chaining."""
        super().remove(item)
        return self

    def reverse(self) -> BaseList:
        """Same as list.reverse(), but returns self and thus allows chaining."""
        super().reverse()
        return self

    def sort(self, *args: Any, **kwargs: Any) -> BaseList:
        """Same as list.sort(), but returns self and thus allows chaining."""
        super().sort(*args, **kwargs)
        return self

    def clear(self) -> BaseList:
        """Same as list.clear(), but returns self and thus allows chaining."""
        super().clear()
        return self

    def copy(self) -> BaseList:
        return type(self)(self)


class List(BaseList, metaclass=TranslatableMeta):
    """
    Subclass of the builtin 'list' class with additional useful methods. All the 'list' class inplace methods return self and therefore allow chaining when called from this class.
    Recursively traverses its members and converts any str, list and dict instances into into their subtypes equivalents.
    """

    class Accessors(Settings):
        slice = SliceAccessor

    def __init__(self, iterable: Iterable = None) -> None:
        super().__init__(iterable) if iterable is not None else super().__init__()

        for index, val in enumerate(self):
            self[index] = type(self).translator.translate(val)

    @cached_property
    def slice(self) -> SliceAccessor:
        return self.Accessors.slice(parent=self)

    @cached_property
    def attr(self) -> AttributeAccessor:
        return AttributeAccessor(self)

    def apply(self, func: Callable) -> List:
        return type(self)(map(func, self))

    def one(self) -> Any:
        if len(self) == 1:
            return self[0]
        else:
            raise ValueError(f"Expected {self} to contain a single value, but actual length was {len(self)}.")

    def one_or_none(self) -> Any:
        if not self:
            return None
        elif len(self) == 1:
            return self[0]
        else:
            raise ValueError(f"Expected {self} to contain a single value or be empty, but actual length was {len(self)}.")

    def split_into_batches(self, num_batches: int) -> Iterator[List]:
        """Split this container into 'num_batches' equally sized containers of the same type. If the length of this container is not perfectly divisible by 'num_batches', the final container will be longer than the rest."""
        if num_batches >= len(self):
            yield type(self)(self)
        else:
            batch_size, final_batch_size_extra = len(self) // num_batches, len(self) % num_batches

            if not final_batch_size_extra:
                for run in range(0, len(self), batch_size):
                    yield self[run:run + batch_size]
            else:
                for run in range(0, (final_batch_position := batch_size*(num_batches - 1)), batch_size):
                    yield self[run:run + batch_size]

                yield self[final_batch_position:]

    def split_into_batches_of_size(self, batch_size: int) -> Iterator[List]:
        """Split this container into smaller containers of the same type of size 'batch_size'. If the length of this container is not perfectly divisible by 'batch_size', the final container will be shorter than the rest."""
        if batch_size >= len(self):
            yield type(self)(self)
        else:
            for run in range(0, len(self), batch_size):
                yield self[run:run + batch_size]

    def to_json(self, indent: int = 4, **kwargs: Any) -> str:
        return json.dumps(self, indent=indent, **kwargs)

    def flatten(self) -> List:
        """Recursively traverses any non-textual Sequence objects within this List and unpacks them in order into a new flat List."""
        return self._flatten_more(iterable=self, output=type(self)())

    def _flatten_more(self, iterable: Iterable, output: List) -> List:
        for item in iterable:
            if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                self._flatten_more(iterable=item, output=output)
            else:
                output.append(item)

        return output

    @classmethod
    def from_json(cls, json_string: str, **kwargs: Any) -> List:
        item = json.loads(json_string, **kwargs)
        if isinstance(item, list):
            return cls(item)
        else:
            raise TypeError(f"The following json string resolves to type '{type(item).__name__}', not type '{list.__name__}':\n\n{json_string}")
