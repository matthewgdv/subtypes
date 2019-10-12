from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup


class Markup(BeautifulSoup):
    """A subclass of bs4.BeautifulSoup which uses 'html.parser' as its default parser."""

    def __init__(self, markup: str, features: str = "html.parser", **kwargs: Any) -> None:
        super().__init__(markup=markup, features=features, **kwargs)
