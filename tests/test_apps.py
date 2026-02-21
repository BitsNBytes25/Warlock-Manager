"""Tests for BaseApp and SteamApp."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from warlock_manager import BaseApp, SteamApp


class ConcreteApp(BaseApp):
    """Minimal concrete subclass for testing BaseApp."""

    def start(self) -> None:
        self._process = MagicMock()
        self._process.poll.return_value = None

    def stop(self) -> None:
        self._process = None


class TestBaseApp:
    def test_repr(self):
        app = ConcreteApp("MyApp", "/opt/myapp")
        assert "MyApp" in repr(app)
        assert "/opt/myapp" in repr(app)

    def test_is_running_initially_false(self):
        app = ConcreteApp("MyApp", "/opt/myapp")
        assert not app.is_running()

    def test_is_running_after_start(self):
        app = ConcreteApp("MyApp", "/opt/myapp")
        app.start()
        assert app.is_running()

    def test_is_running_after_stop(self):
        app = ConcreteApp("MyApp", "/opt/myapp")
        app.start()
        app.stop()
        assert not app.is_running()

    def test_restart_calls_stop_then_start(self):
        app = ConcreteApp("MyApp", "/opt/myapp")
        app.start()
        app.restart()
        assert app.is_running()


class TestSteamApp:
    def _make_app(self, **kwargs):
        defaults = dict(
            name="ValheimServer",
            install_dir="/opt/valheim",
            app_id=896660,
        )
        defaults.update(kwargs)
        return SteamApp(**defaults)

    def test_repr(self):
        app = self._make_app()
        r = repr(app)
        assert "ValheimServer" in r
        assert "896660" in r

    def test_install_calls_steamcmd(self):
        app = self._make_app()
        with patch("subprocess.run") as mock_run:
            app.install()
            mock_run.assert_called_once()
            cmd = mock_run.call_args.args[0]
            assert "+app_update" in cmd
            assert "896660" in cmd

    def test_install_validate_appends_validate(self):
        app = self._make_app()
        with patch("subprocess.run") as mock_run:
            app.install(validate=True)
            cmd = mock_run.call_args.args[0]
            assert "validate" in cmd

    def test_update_calls_install_with_validate(self):
        app = self._make_app()
        with patch.object(app, "install") as mock_install:
            app.update()
            mock_install.assert_called_once_with(validate=True)

    def test_start_launches_process(self):
        app = self._make_app(executable="/opt/valheim/valheim_server", launch_args=["-nographics"])
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(**{"poll.return_value": None})
            app.start()
            mock_popen.assert_called_once()
            assert app.is_running()

    def test_start_does_not_duplicate_if_running(self):
        app = self._make_app(executable="/opt/valheim/valheim_server")
        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(**{"poll.return_value": None})
            app.start()
            app.start()  # second call should be a no-op
            mock_popen.assert_called_once()

    def test_stop_terminates_process(self):
        app = self._make_app(executable="/opt/valheim/valheim_server")
        mock_proc = MagicMock(**{"poll.return_value": None})
        app._process = mock_proc
        app.stop()
        mock_proc.terminate.assert_called_once()
        mock_proc.wait.assert_called_once()
        assert app._process is None
