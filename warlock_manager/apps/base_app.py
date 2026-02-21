import logging
import subprocess
from abc import ABC, abstractmethod


class BaseApp(ABC):
    """Base class for application management."""

    def __init__(self, name: str, install_dir: str):
        self.name = name
        self.install_dir = install_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        self._process: subprocess.Popen | None = None

    @abstractmethod
    def start(self) -> None:
        """Start the application."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the application."""

    def restart(self) -> None:
        """Restart the application."""
        self.stop()
        self.start()

    def is_running(self) -> bool:
        """Return True if the application process is currently running."""
        return self._process is not None and self._process.poll() is None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, install_dir={self.install_dir!r})"
