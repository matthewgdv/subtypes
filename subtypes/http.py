from __future__ import annotations

from typing import Any

import requests


class Http(requests.Session):
    """Subclass of requests.Session which takes a 'base_url' constructor argument and prepends it to all future requests."""

    def __init__(self, base_url: str = "") -> None:
        super().__init__()
        self.base_url = base_url

    def __repr__(self) -> str:
        return f"{type(self).__name__}(base_url={repr(self.base_url)}, auth={repr(self.auth)}, headers={repr(self.headers)})"

    def request(self, method: str, url: str, *args: Any, **kwargs: Any) -> Any:
        return super().request(method=method, url=f"{self.base_url.strip('/')}/{url.strip('/')}", *args, **kwargs)
