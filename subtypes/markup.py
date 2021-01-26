from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, Tag
from prettierfier import prettify_html
import html_text
from xml.dom.minidom import parseString as parse_xml

from .str import Str


class Markup(BeautifulSoup):
    """A subclass of bs4.BeautifulSoup which uses 'lxml' as its default parser."""

    _stack = []
    parser = None

    def __init__(self, html: str = None, features: str = None, **kwargs: Any) -> None:
        kwargs["element_classes"] = {**{Tag: self.Tag}, **kwargs.get("element_classes", {})}
        super().__init__(markup=html or "", features=features or self.parser, **kwargs)

    def __repr__(self, encoding="unicode-escape") -> str:
        return str(self)

    def __enter__(self) -> Markup:
        self._stack.append(self)
        return self

    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        self._stack.pop()

    def tag(self, name: str, content: str = None, /, attrs: dict = None, **kwattrs: Any) -> Markup.Tag:
        tag = self.new_tag(name=name, attrs=attrs or {}, **kwattrs)

        if content:
            tag.string = content

        if self._stack:
            self._stack[-1].append(tag)
        else:
            self.append(tag)

        return tag

    @property
    def text(self) -> str:
        return html_text.extract_text(str(self))

    class Tag(Tag):
        def __enter__(self) -> Tag:
            self._stack.append(self)
            return self

        def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
            self._stack.pop()


class Html(Markup):
    _stack = []
    parser = "lxml"

    def __str__(self) -> str:
        return Str(prettify_html(self.prettify())).re(multiline=True).sub(r"^( +)", lambda m: m.group(1)*4)


class Xml(Markup):
    """A subclass of bs4.BeautifulSoup which uses 'xml.parser' as its default parser."""

    _stack = []
    parser = "xml"

    def __str__(self) -> str:
        return Str(parse_xml(super().__str__()).toprettyxml()).re(multiline=True).sub(r"^(\t+)", lambda m: m.group(1).replace("\t", "    "))
