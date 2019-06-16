from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup


class Markup(BeautifulSoup):
    def __init__(self, *args: Any, parser: str = "html.parser", **kwargs: Any) -> None:
        super().__init__(args[0], parser, *args[1:], **kwargs)
