import socket
import struct

from .base_service import BaseService, ServiceStatus

# RCON packet types (Valve Source RCON protocol)
_PACKET_TYPE_AUTH = 3
_PACKET_TYPE_AUTH_RESPONSE = 2
_PACKET_TYPE_EXEC = 2
_PACKET_TYPE_RESPONSE = 0

_AUTH_FAILURE_ID = -1


class RconError(Exception):
    """Raised when an RCON operation fails."""


class RconService(BaseService):
    """Service that communicates with a game server via the RCON protocol."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        password: str,
        timeout: float = 5.0,
    ):
        super().__init__(name)
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self._socket: socket.socket | None = None
        self._request_id = 0

    def start(self) -> None:
        """Connect to the RCON server and authenticate."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(self.timeout)
        try:
            self._socket.connect((self.host, self.port))
            self._authenticate()
            self._status = ServiceStatus.RUNNING
            self.logger.info("RCON connected to %s:%s.", self.host, self.port)
        except (OSError, RconError) as exc:
            self._status = ServiceStatus.ERROR
            self._close_socket()
            self.logger.error("RCON connection failed: %s", exc)
            raise

    def stop(self) -> None:
        """Disconnect from the RCON server."""
        self._close_socket()
        self._status = ServiceStatus.STOPPED
        self.logger.info("RCON disconnected from %s:%s.", self.host, self.port)

    def execute(self, command: str) -> str:
        """Send a command to the server and return the response."""
        if not self.is_running() or self._socket is None:
            raise RconError("Not connected. Call start() first.")
        request_id = self._next_id()
        self._send_packet(request_id, _PACKET_TYPE_EXEC, command)
        return self._read_response(request_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_id(self) -> int:
        self._request_id = (self._request_id % 0x7FFFFFFF) + 1
        return self._request_id

    def _authenticate(self) -> None:
        request_id = self._next_id()
        self._send_packet(request_id, _PACKET_TYPE_AUTH, self.password)
        # Read (and discard) the empty SERVERDATA_RESPONSE_VALUE packet
        self._recv_packet()
        # Read the auth response packet
        resp_id, _, _ = self._recv_packet()
        if resp_id == _AUTH_FAILURE_ID:
            raise RconError("RCON authentication failed: bad password.")

    def _send_packet(self, request_id: int, packet_type: int, body: str) -> None:
        encoded = body.encode("utf-8")
        # Packet: size (int32) + id (int32) + type (int32) + body + 2 null bytes
        payload = struct.pack("<ii", request_id, packet_type) + encoded + b"\x00\x00"
        size = struct.pack("<i", len(payload))
        assert self._socket is not None
        self._socket.sendall(size + payload)

    def _recv_packet(self) -> tuple[int, int, str]:
        assert self._socket is not None
        size_data = self._recv_exactly(4)
        (size,) = struct.unpack("<i", size_data)
        data = self._recv_exactly(size)
        request_id, packet_type = struct.unpack("<ii", data[:8])
        body = data[8:-2].decode("utf-8", errors="replace")
        return request_id, packet_type, body

    def _recv_exactly(self, length: int) -> bytes:
        assert self._socket is not None
        buf = b""
        while len(buf) < length:
            chunk = self._socket.recv(length - len(buf))
            if not chunk:
                raise RconError("Connection closed by server.")
            buf += chunk
        return buf

    def _read_response(self, request_id: int) -> str:
        resp_id, _, body = self._recv_packet()
        if resp_id != request_id:
            raise RconError(
                f"Response ID mismatch: expected {request_id}, got {resp_id}."
            )
        return body

    def _close_socket(self) -> None:
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def __repr__(self) -> str:
        return (
            f"RconService(name={self.name!r}, host={self.host!r}, "
            f"port={self.port!r}, status={self._status!r})"
        )
