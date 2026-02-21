"""Tests for BaseService, HttpService, and RconService."""

import socket
import struct
from unittest.mock import MagicMock, patch

import pytest

from warlock_manager import BaseService, HttpService, RconError, RconService, ServiceStatus


# ---------------------------------------------------------------------------
# BaseService helpers
# ---------------------------------------------------------------------------

class ConcreteService(BaseService):
    def start(self) -> None:
        self._status = ServiceStatus.RUNNING

    def stop(self) -> None:
        self._status = ServiceStatus.STOPPED


class TestBaseService:
    def test_initial_status_stopped(self):
        svc = ConcreteService("test")
        assert svc.status == ServiceStatus.STOPPED
        assert not svc.is_running()

    def test_start_sets_running(self):
        svc = ConcreteService("test")
        svc.start()
        assert svc.is_running()

    def test_stop_sets_stopped(self):
        svc = ConcreteService("test")
        svc.start()
        svc.stop()
        assert svc.status == ServiceStatus.STOPPED

    def test_restart(self):
        svc = ConcreteService("test")
        svc.start()
        svc.restart()
        assert svc.is_running()

    def test_repr(self):
        svc = ConcreteService("mysvc")
        assert "mysvc" in repr(svc)


# ---------------------------------------------------------------------------
# HttpService
# ---------------------------------------------------------------------------

class TestHttpService:
    def _make_svc(self, **kwargs):
        defaults = dict(name="api", base_url="http://example.com")
        defaults.update(kwargs)
        return HttpService(**defaults)

    def test_repr(self):
        svc = self._make_svc()
        r = repr(svc)
        assert "api" in r
        assert svc.base_url in r

    def test_start_sets_running_on_success(self):
        svc = self._make_svc()
        with patch.object(svc._session, "get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            svc.start()
        assert svc.is_running()

    def test_start_sets_error_on_failure(self):
        import requests
        svc = self._make_svc()
        with patch.object(svc._session, "get", side_effect=requests.ConnectionError()):
            with pytest.raises(requests.ConnectionError):
                svc.start()
        assert svc.status == ServiceStatus.ERROR

    def test_stop_sets_stopped(self):
        svc = self._make_svc()
        with patch.object(svc._session, "get"):
            svc.start()
        svc.stop()
        assert svc.status == ServiceStatus.STOPPED

    def test_get_request(self):
        svc = self._make_svc()
        with patch.object(svc._session, "get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            resp = svc.get("/api/data")
        mock_get.assert_called_once()
        url_called = mock_get.call_args.args[0]
        assert "api/data" in url_called

    def test_post_request(self):
        svc = self._make_svc()
        with patch.object(svc._session, "post") as mock_post:
            mock_post.return_value = MagicMock(status_code=201)
            svc.post("/api/items", json={"key": "value"})
        mock_post.assert_called_once()

    def test_base_url_trailing_slash_stripped(self):
        svc = self._make_svc(base_url="http://example.com/")
        assert not svc.base_url.endswith("/")

    def test_custom_headers_forwarded(self):
        svc = self._make_svc(headers={"X-Token": "abc"})
        assert svc._session.headers.get("X-Token") == "abc"


# ---------------------------------------------------------------------------
# RconService
# ---------------------------------------------------------------------------

def _build_packet(request_id: int, ptype: int, body: str) -> bytes:
    encoded = body.encode("utf-8")
    payload = struct.pack("<ii", request_id, ptype) + encoded + b"\x00\x00"
    size = struct.pack("<i", len(payload))
    return size + payload


class TestRconService:
    def _make_svc(self, **kwargs):
        defaults = dict(
            name="mc",
            host="127.0.0.1",
            port=25575,
            password="secret",
        )
        defaults.update(kwargs)
        return RconService(**defaults)

    def test_repr(self):
        svc = self._make_svc()
        r = repr(svc)
        assert "mc" in r
        assert "25575" in r

    def test_execute_raises_when_not_connected(self):
        svc = self._make_svc()
        with pytest.raises(RconError):
            svc.execute("help")

    def test_start_and_authenticate(self):
        svc = self._make_svc()
        # Auth response packet (id=1, type=2) then command response
        auth_empty = _build_packet(1, 0, "")   # empty SERVERDATA_RESPONSE_VALUE
        auth_ok = _build_packet(1, 2, "")       # auth OK
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            # _recv_exactly for auth_empty size
            auth_empty[:4],
            auth_empty[4:],
            # _recv_exactly for auth_ok size
            auth_ok[:4],
            auth_ok[4:],
        ]
        with patch("socket.socket", return_value=mock_sock):
            svc.start()
        assert svc.is_running()

    def test_start_fails_on_bad_password(self):
        svc = self._make_svc()
        auth_empty = _build_packet(1, 0, "")
        auth_fail = _build_packet(-1, 2, "")
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            auth_empty[:4], auth_empty[4:],
            auth_fail[:4], auth_fail[4:],
        ]
        with patch("socket.socket", return_value=mock_sock):
            with pytest.raises(RconError, match="authentication failed"):
                svc.start()
        assert svc.status == ServiceStatus.ERROR

    def test_execute_sends_command_and_returns_response(self):
        svc = self._make_svc()
        auth_empty = _build_packet(1, 0, "")
        auth_ok = _build_packet(1, 2, "")
        cmd_resp = _build_packet(2, 0, "pong")
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            auth_empty[:4], auth_empty[4:],
            auth_ok[:4], auth_ok[4:],
            cmd_resp[:4], cmd_resp[4:],
        ]
        with patch("socket.socket", return_value=mock_sock):
            svc.start()
            result = svc.execute("ping")
        assert result == "pong"

    def test_stop_closes_socket(self):
        svc = self._make_svc()
        auth_empty = _build_packet(1, 0, "")
        auth_ok = _build_packet(1, 2, "")
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            auth_empty[:4], auth_empty[4:],
            auth_ok[:4], auth_ok[4:],
        ]
        with patch("socket.socket", return_value=mock_sock):
            svc.start()
        svc.stop()
        mock_sock.close.assert_called_once()
        assert svc.status == ServiceStatus.STOPPED
