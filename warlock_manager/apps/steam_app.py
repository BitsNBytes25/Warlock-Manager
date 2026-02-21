import os
import subprocess

from .base_app import BaseApp


class SteamApp(BaseApp):
    """Application managed via SteamCMD (e.g. dedicated game servers)."""

    def __init__(
        self,
        name: str,
        install_dir: str,
        app_id: int,
        steamcmd_path: str = "steamcmd",
        executable: str = "",
        launch_args: list[str] | None = None,
    ):
        super().__init__(name, install_dir)
        self.app_id = app_id
        self.steamcmd_path = steamcmd_path
        self.executable = executable
        self.launch_args = launch_args or []

    def install(self, validate: bool = False) -> None:
        """Install or update the app via SteamCMD."""
        cmd = [
            self.steamcmd_path,
            "+force_install_dir", self.install_dir,
            "+login", "anonymous",
            "+app_update", str(self.app_id),
        ]
        if validate:
            cmd.append("validate")
        cmd.append("+quit")
        self.logger.info("Running SteamCMD: %s", " ".join(cmd))
        subprocess.run(cmd, check=True)

    def update(self) -> None:
        """Update the app (alias for install with validate)."""
        self.install(validate=True)

    def start(self) -> None:
        """Start the game server process."""
        if self.is_running():
            self.logger.warning("%s is already running.", self.name)
            return
        exe = self.executable or os.path.join(self.install_dir, self.name)
        cmd = [exe] + self.launch_args
        self.logger.info("Starting %s: %s", self.name, " ".join(cmd))
        self._process = subprocess.Popen(cmd, cwd=self.install_dir)

    def stop(self) -> None:
        """Stop the game server process."""
        if self._process and self.is_running():
            self.logger.info("Stopping %s.", self.name)
            self._process.terminate()
            self._process.wait()
        self._process = None

    def __repr__(self) -> str:
        return (
            f"SteamApp(name={self.name!r}, app_id={self.app_id!r}, "
            f"install_dir={self.install_dir!r})"
        )
