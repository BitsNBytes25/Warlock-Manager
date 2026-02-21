import logging
from abc import ABC, abstractmethod
from enum import Enum


class ServiceStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"


class BaseService(ABC):
    """Base class for service abstractions."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
        self._status = ServiceStatus.STOPPED

    @property
    def status(self) -> ServiceStatus:
        """Current status of the service."""
        return self._status

    @abstractmethod
    def start(self) -> None:
        """Start the service."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the service."""

    def restart(self) -> None:
        """Restart the service."""
        self.stop()
        self.start()

    def is_running(self) -> bool:
        """Return True if the service is currently running."""
        return self._status == ServiceStatus.RUNNING

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, status={self._status!r})"
