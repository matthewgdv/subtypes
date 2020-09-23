from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, Tag
from prettierfier import prettify_html
import html_text

from .str import Str


class Html(BeautifulSoup):
    """A subclass of bs4.BeautifulSoup which uses 'html.parser' as its default parser."""

    _stack = []

    def __init__(self, html: str = None, features: str = "html.parser", **kwargs: Any) -> None:
        element_classes = kwargs.get("element_classes", {})
        element_classes[Tag] = Html.Tag
        kwargs["element_classes"] = element_classes

        super().__init__(markup=html or "", features=features, **kwargs)

    def __repr__(self, encoding="unicode-escape") -> str:
        return str(self)

    def __str__(self) -> str:
        return Str(prettify_html(self.prettify())).re(multiline=True).sub(r"^( +)", lambda m: m.group(1)*4)

    def __enter__(self) -> Html:
        Html._stack.append(self)
        return self

    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        Html._stack.pop()

    def tag(self, name: str, content: str = None, /, attrs: dict = None, **kwattrs: Any) -> Html.Tag:
        tag = self.new_tag(name=name, attrs=attrs or {}, **kwattrs)

        if content:
            tag.string = content

        if Html._stack:
            Html._stack[-1].append(tag)
        else:
            self.append(tag)

        return tag

    @property
    def text(self) -> str:
        return html_text.extract_text(str(self))

    class Tag(Tag):
        def __enter__(self) -> Tag:
            Html._stack.append(self)
            return self

        def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
            Html._stack.pop()
