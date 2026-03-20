import os
import sys
import subprocess
import time
from abc import ABC
import logging

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

	def watch(self, callback, timeout: int = 10) -> bool:
		"""
		Watch the systemd journal output for this service and call a callback function for each line.

		The callback function should accept a single string argument (the journal line) and return True
		when it has found the expected output, False to continue watching.

		:param callback: Function that receives journal lines and returns True when watch is complete
		:param timeout: Maximum time to watch in seconds (default: 10)
		:return: True if callback signaled completion, False if timeout occurred
		"""

		start_time = time.time()
		try:
			# Start journalctl following from now on, for this service only
			process = subprocess.Popen(
				['journalctl', '-u', self.service, '-f', '--no-pager'],
				stdout=subprocess.PIPE,
				stderr=subprocess.DEVNULL,
				encoding='utf-8',
				bufsize=1
			)

			while True:
				# Check if timeout has been exceeded
				if time.time() - start_time > timeout:
					process.terminate()
					try:
						process.wait(timeout=2)
					except subprocess.TimeoutExpired:
						process.kill()
					return False

				# Read the next line from journal
				line = process.stdout.readline()
				if not line:
					# Process ended unexpectedly
					return False

				line = line.rstrip('\n')

				# Call the callback function with the journal line
				try:
					if callback(line):
						# Callback signaled completion
						process.terminate()
						try:
							process.wait(timeout=2)
						except subprocess.TimeoutExpired:
							process.kill()
						return True
				except Exception as e:
					logging.error('Error in watch callback: %s' % str(e))
					process.terminate()
					try:
						process.wait(timeout=2)
					except subprocess.TimeoutExpired:
						process.kill()
					raise

		except Exception as e:
			logging.error('Error while watching journal: %s' % str(e))
			return False

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
