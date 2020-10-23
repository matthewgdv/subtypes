from __future__ import annotations

from typing import Any
import json
import simplejson

from requests import Session
import requests.models
from requests.compat import quote, quote_plus

from .enums import Enum
from .translator import Translator


class Response(requests.models.Response):
    """Subclass of requests.Response with a modified Response.json() method."""

    def __init__(self, namespace: dict) -> None:
        self.__dict__ = namespace

    def json(self) -> Any:
        """Returns Str, List, and Dict items rather than their builtin superclasses. If there is no data will return None rather than raising JSONDecodeError."""
        try:
            return Translator.default.translate(super().json())
        except (json.JSONDecodeError, simplejson.JSONDecodeError):
            return None


class Http(Session):
    """
    Subclass of requests.Session which takes a 'base_url' constructor argument and prepends it to all future requests.
    It returns Str, List, and Dict instances when deserializing json from responses and can automatically quote all urls passed to its http methods.
    """

    class QuoteLevel(Enum):
        NONE, NORMAL, PLUS = "none", "normal", "plus"

    def __init__(self, base_url: str = "", quote_level: Http.QuoteLevel = QuoteLevel.NONE) -> None:
        super().__init__()
        self.base_url, self.quote_level = base_url.strip('/'), quote_level

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={repr(self.base_url)}, auth={repr(self.auth)}, headers={repr(self.headers)})"

    def request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Any:
        return Response(super().request(method=method, url=self._quote_encode(f"""{f"{self.base_url}/{url.strip('/')}".strip("/")}/"""), *args, **kwargs).__dict__)

    def _quote_encode(self, url: str) -> str:
        return self.QuoteLevel(self.quote_level).map_to({
            self.QuoteLevel.NONE: lambda url_: url_,
            self.QuoteLevel.NORMAL: lambda url_: quote(url_),
            self.QuoteLevel.PLUS: lambda url_: quote_plus(url_),
        })()
