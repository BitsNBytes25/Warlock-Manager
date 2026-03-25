import socket
import psutil


def get_listening_port(port: int, protocol: str) -> dict | None:
	"""
	Get the psutil definition for the listening port, or None if it's not open

	If found, it returns a dictionary with the following keys:

	pid: The PID of the listening process
	ip: The IP address of the listening process (usually either 0.0.0.0, ::, 127.0.0.1, or an IP address)
	status: The status of the listening process (e.g., LISTEN, TIME_WAIT, etc.)

	:param port: Port number (1-65535)
	:param protocol: Protocol, either TCP or UDP
	:return:
	"""
	if protocol.upper() == 'TCP':
		check_type = socket.SOCK_STREAM
	else:
		check_type = socket.SOCK_DGRAM

	if port < 1 or port > 65535:
		# Invalid port number
		return None

	connections = psutil.net_connections(kind='inet')
	for connection in connections:
		if connection.laddr.port == port and connection.type == check_type:
			if check_type == socket.SOCK_STREAM and connection.status == 'LISTEN':
				# TCP connections have registered LISTEN status
				return _standardize_connection(connection)
			elif check_type == socket.SOCK_DGRAM:
				# UDP connections are just ...... there.
				return _standardize_connection(connection)

	return None


def get_ports(protocol: str) -> set[int]:
	"""
	Get all listening ports for the given protocol

	:param protocol: Protocol, either TCP or UDP
	:return:
	"""
	if protocol.upper() == 'TCP':
		check_type = socket.SOCK_STREAM
	else:
		check_type = socket.SOCK_DGRAM

	ports = set()

	connections = psutil.net_connections(kind='inet')
	for connection in connections:
		if connection.type == check_type:
			if check_type == socket.SOCK_STREAM and connection.status == 'LISTEN':
				# TCP connections have registered LISTEN status
				ports.add(connection.laddr.port)
			elif check_type == socket.SOCK_DGRAM:
				# UDP connections are just ...... there.
				ports.add(connection.laddr.port)

	return ports


def _standardize_connection(connection) -> dict:
	return {
		'pid': connection.pid,
		'ip': connection.laddr.ip,
		'status': connection.status,
	}
