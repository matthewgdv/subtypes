from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup, Tag
from prettierfier import prettify_html
import html_text
from xml.dom.minidom import parseString as parse_xml

from .str import Str


class Markup(BeautifulSoup):
    """A base class for BeautifulSoup markup classes to inherit from."""

    parser = None

    def __init__(self, html: str = None, features: str = None, **kwargs: Any) -> None:
        kwargs["element_classes"] = {**{Tag: self.Tag}, **kwargs.get("element_classes", {})}
        super().__init__(markup=html or "", features=features or self.parser, **kwargs)
        self.tag = TagAccessor(self)
        self._stack = []

    def __repr__(self, encoding="unicode-escape") -> str:
        return str(self)

    def __enter__(self) -> Markup:
        self._stack.append(self)
        return self

    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        self._stack.pop()

    def _tag(self, name: str, content: str = None, /, attrs: dict = None, **kwattrs: Any) -> Markup.Tag:
        tag = self.new_tag(name=name, attrs=attrs or {}, **kwattrs)
        tag._root = self

        if content:
            tag.string = content

        if self._stack:
            self._stack[-1].append(tag)
        else:
            self.append(tag)

        return tag

    class Tag(Tag):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._root = None

        def __enter__(self) -> Markup.Tag:
            self._root._stack.append(self)
            return self

        def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
            self._root._stack.pop()


class Html(Markup):
    """A subclass of bs4.BeautifulSoup which uses 'lxml' as its default parser."""

    parser = "lxml"

    def __str__(self) -> str:
        return Str(prettify_html(self.prettify())).re(multiline=True).sub(r"^( +)", lambda m: m.group(1)*4)

    @property
    def text(self) -> str:
        return html_text.extract_text(str(self))


class Xml(Markup):
    """A subclass of bs4.BeautifulSoup which uses 'xml' as its default parser."""

    parser = "xml"

    def __str__(self) -> str:
        return Str(parse_xml(super().__str__()).toprettyxml()).re(multiline=True).sub(r"^(\t+)", lambda m: m.group(1).replace("\t", "    "))


class TagAccessor:
    def __init__(self, parent: Markup) -> None:
        self._parent = parent

    def __call__(self, name: str, content: str = None, /, attrs: dict = None, **kwattrs: Any) -> Markup.Tag:
        return self._parent._tag(name, content, attrs=attrs, **kwattrs)

    def __getattr__(self, name) -> TagProxy:
        return TagProxy(name, parent=self._parent)


class TagProxy:
    def __init__(self, name: str, parent: Markup) -> None:
        self._name, self._parent = name, parent

    def __call__(self, content: str = None, /, attrs: dict = None, **kwattrs: Any) -> Markup.Tag:
        return self._parent._tag(self._name, content, attrs=attrs, **kwattrs)

    def __enter__(self) -> Markup.Tag:
        return self._parent._tag(self._name).__enter__()

    def __exit__(self, ex_type: Any, ex_value: Any, ex_traceback: Any) -> None:
        pass
