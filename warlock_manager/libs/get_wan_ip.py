from typing import Union
from urllib import request
from urllib import error as urllib_error


def get_wan_ip() -> Union[str, None]:
	"""
	Get the external IP address of this server
	:return: str: The external IP address as a string, or None if it cannot be determined
	"""
	try:
		with request.urlopen('https://api.ipify.org', timeout=2) as resp:
			return resp.read().decode('utf-8')
	except (urllib_error.HTTPError, urllib_error.URLError):
		try:
			with request.urlopen('http://wan.eval.bz', timeout=2) as resp:
				return resp.read().decode('utf-8')
		except (urllib_error.HTTPError, urllib_error.URLError):
			return None
