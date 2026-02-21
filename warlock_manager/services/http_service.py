from typing import Any

import requests

from .base_service import BaseService, ServiceStatus


class HttpService(BaseService):
    """Service that communicates over HTTP/HTTPS."""

    def __init__(
        self,
        name: str,
        base_url: str,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
    ):
        super().__init__(name)
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(self.headers)

    def start(self) -> None:
        """Mark the service as running and verify connectivity."""
        try:
            self._session.get(self.base_url, timeout=self.timeout)
            self._status = ServiceStatus.RUNNING
            self.logger.info("%s is reachable at %s.", self.name, self.base_url)
        except requests.RequestException as exc:
            self._status = ServiceStatus.ERROR
            self.logger.error("Failed to reach %s: %s", self.base_url, exc)
            raise

    def stop(self) -> None:
        """Close the HTTP session."""
        self._session.close()
        self._session = requests.Session()
        self._session.headers.update(self.headers)
        self._status = ServiceStatus.STOPPED
        self.logger.info("%s session closed.", self.name)

    def get(self, path: str = "", **kwargs: Any) -> requests.Response:
        """Perform a GET request."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        return self._session.get(url, timeout=self.timeout, **kwargs)

    def post(self, path: str = "", **kwargs: Any) -> requests.Response:
        """Perform a POST request."""
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        return self._session.post(url, timeout=self.timeout, **kwargs)

    def __repr__(self) -> str:
        return (
            f"HttpService(name={self.name!r}, base_url={self.base_url!r}, "
            f"status={self._status!r})"
        )
