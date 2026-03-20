import os
import sys
from abc import ABC

from SystemdUnitParser import SystemdUnitParser
from typing_extensions import deprecated

from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService


class SocketService(BaseService, ABC):

	def __init__(self, service: str, game: BaseApp):
		super().__init__(service, game)

		self.socket: str = '/var/run/%s.socket' % self.service
		"""
		Socket path for this service, must be set for the API to function.

		Set by default to /var/run/{service}.socket, but can be overridden by the service implementation if needed.
		"""

	@deprecated('use cmd instead')
	def _api_cmd(self, cmd: str):
		return self.cmd(cmd)

	def cmd(self, cmd) -> None | str:
		"""
		Send a command to the game server via its Systemd socket

		:param cmd:
		:return:
		"""
		if not self.is_api_enabled():
			print("API is not enabled for this service, unable to send command.", file=sys.stderr)
			return None

		with open(self.socket, 'w') as f:
			f.write(cmd + '\n')

		return 'Sent command'

	def is_api_enabled(self) -> bool:
		"""
		Check if API is enabled for this service
		:return:
		"""

		# This game uses sockets for API communication, so it's always enabled if the socket file exists
		return self.socket and os.path.exists(self.socket)

	def get_systemd_config(self) -> SystemdUnitParser:
		"""
		Get the systemd unit configuration for this service, if available
		:return:
		"""
		config = super().get_systemd_config()

		if not self.socket:
			return config

		config['Service']['Sockets'] = os.path.basename(self.socket)
		config['Service']['StandardInput'] = 'socket'
		config['Service']['StandardOutput'] = 'journal'
		config['Service']['StandardError'] = 'journal'

		return config

	def build_systemd_socket(self):
		if not self.socket:
			return

		path = os.path.join('/etc/systemd/system', os.path.basename(self.socket))

		config = SystemdUnitParser()
		if os.path.exists(path):
			config.read(path)

		# Load default sections that are required
		if 'Unit' not in config:
			config['Unit'] = {}
		if 'Socket' not in config:
			config['Socket'] = {}

		# Populate the configuration with this environment
		config['Unit']['BindsTo'] = os.path.basename(self._service_file)
		config['Socket']['ListenFIFO'] = self.socket
		config['Socket']['Service'] = os.path.basename(self._service_file)
		config['Socket']['RemoveOnStop'] = 'true'
		config['Socket']['SocketMode'] = '0660'
		config['Socket']['SocketUser'] = str(self.game.get_app_uid())

		with open(path, 'w') as f:
			config.write(f)
