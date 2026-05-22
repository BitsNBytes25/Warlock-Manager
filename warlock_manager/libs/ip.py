import socket
import psutil
from urllib import request
from urllib import error as urllib_error


def get_local_ip() -> str | None:
	"""
	Get the local IP address used for global communication

	Connects to a known external address (like Google's DNS server)
	and retrieves the local IP address associated with that connection.
	This is generally more reliable than just using socket.gethostbyname(socket.gethostname()).
	"""
	sock = None
	try:
		# Create a socket object
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# Connect the socket to a server (doesn't actually send data, just establishes the route)
		# We use Google's public DNS server address here as an example.
		sock.connect(("8.8.8.8", 80))

		# Once connected, we ask the socket for its local IP address
		local_ip = sock.getsockname()[0]
		return local_ip
	except Exception:
		return None
	finally:
		# Always close the socket when done! Good housekeeping!
		if sock:
			sock.close()


def get_local_ips() -> list[str]:
	"""
	Get a list of all local IP addresses

	:return: List of all IP addresses on the local system
	"""
	ret = []
	for device, addrs in psutil.net_if_addrs().items():
		for addr in addrs:
			if addr.family == socket.AF_INET:
				ret.append(addr.address)

	return ret


def get_wan_ip() -> str | None:
	"""
	Get the external (WAN) IP address of this server
	:return: str: The external IP address as a string, or None if it cannot be determined
	"""
	try:
		with request.urlopen('http://wan.eval.bz', timeout=2) as resp:
			return resp.read().decode('utf-8')
	except (urllib_error.HTTPError, urllib_error.URLError, TimeoutError):
		try:
			with request.urlopen('https://api.ipify.org', timeout=2) as resp:
				return resp.read().decode('utf-8')
		except (urllib_error.HTTPError, urllib_error.URLError, TimeoutError):
			return None
