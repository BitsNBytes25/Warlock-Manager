import os
import subprocess
import time
from abc import ABC
import threading
from queue import Queue
from typing import Callable, Optional

from SystemdUnitParser import SystemdUnitParser
from typing_extensions import deprecated

from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.logger import logger


class SocketService(BaseService, ABC):

	def __init__(self, service: str, game: BaseApp):
		super().__init__(service, game)

		self.socket: str = '/var/run/%s.socket' % self.service
		"""
		Socket path for this service, must be set for the API to function.

		Set by default to /var/run/{service}.socket, but can be overridden by the service implementation if needed.
		"""

	def create_service(self):
		"""
		Create the systemd service for this game, including the service file and environment file
		:return:
		"""
		super().create_service()

		# Socket-based services require a systemd socket file
		self.build_systemd_socket()
		self.reload()

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
			logger.warning('API is not available for this service right now, unable to send command.')
			return None

		port_open = self.is_port_open()
		if port_open is False:
			logger.warning('Port is not open for this service right now, refusing to send command.')
			return None

		logger.debug('Sending command to %s: %s' % (self.service, cmd))
		with open(self.socket, 'w') as f:
			f.write(cmd + '\n')

		return 'Sent command'

	def write_socket(self, content):
		"""
		Simple write to socket command

		Skips any checks to allow for raw access to the socket,
		only checks if the socket file exists.

		:param content:
		:return:
		"""
		if not self.socket or not os.path.exists(self.socket):
			logger.warning('Socket file %s does not exist, unable to write to it.' % self.socket)
			return

		with open(self.socket, 'w') as f:
			f.write(content + '\n')

	def watch(self, callback: Callable[[str], Optional[bool]], timeout: int = 10) -> bool:
		"""
		Watch the systemd journal output for this service and call a callback function for each line.

		The callback function should accept a single string argument (the journal line) and return:
		- True: Line matched, continue watching and extend timeout by 0.5 seconds
		- False: Found what we need, stop immediately
		- None/other: Line didn't match, keep watching

		:param callback: Function that receives journal lines and returns True/False
		:param timeout: Maximum time to watch in seconds (default: 10)
		:return: True if callback signaled completion (False return), False if timeout occurred
		"""

		# Don't watch if service is already stopped
		if self.is_stopped():
			return False

		# Thread-safe buffer for process output
		output_buffer = Queue()
		stop_event = threading.Event()
		process_exception = []

		def read_process_output():
			"""Thread function: reads from process and puts lines into the buffer"""
			try:
				process = subprocess.Popen(
					['journalctl', '-u', self.service, '-f', '--no-pager', '--since', 'now'],
					stdout=subprocess.PIPE,
					stderr=subprocess.DEVNULL,
					encoding='utf-8',
					bufsize=0
				)
				while not stop_event.is_set():
					line = process.stdout.readline()
					output_buffer.put(line.rstrip())
				else:
					process.terminate()

			except Exception as e:
				logger.error(f'Error starting process: {e}')
				process_exception.append(e)
			finally:
				# Signal end of stream
				output_buffer.put(None)

		# Start the reader thread
		reader_thread = threading.Thread(target=read_process_output, daemon=True)
		reader_thread.start()

		start_time = time.time()
		last_true_time = None

		try:
			while True:
				# Check for overall timeout
				if time.time() - start_time > timeout:
					logger.debug(f'Watch timeout reached ({timeout}s)')
					stop_event.set()
					return False

				# Check for extended timeout (0.5s after last True)
				if last_true_time is not None:
					if time.time() - last_true_time > 0.3:
						logger.debug('Extended timeout reached (0.3s after last True)')
						stop_event.set()
						return False

				# Calculate remaining time for queue.get()
				remaining_overall = timeout - (time.time() - start_time)
				wait_time = min(0.1, max(0.01, remaining_overall))  # Small wait to keep responsive

				try:
					line = output_buffer.get(timeout=wait_time)

					# None signals end of stream from the process
					if line is None:
						stop_event.set()
						return False

					# Call the callback with the journal line
					try:
						response = callback(line)

						if response is False:
							# Callback signaled completion
							logger.debug('Callback returned False, stopping watch')
							stop_event.set()
							return True

						elif response is True:
							# Update the extended timeout
							last_true_time = time.time()
							logger.debug('Callback returned True, extending timeout')

						# None/other: continue watching without extending timeout

					except Exception as e:
						logger.error(f'Error in watch callback: {e}')
						stop_event.set()
						raise

				except Exception:
					# Queue timeout (normal, just continue)
					continue

		finally:
			# Ensure the reader thread stops
			stop_event.set()
			reader_thread.join(timeout=0.3)

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

		logger.info('Created systemd socket for %s at %s' % (self.service, path))

	def remove_service(self):
		"""
		Remove the systemd service for this game, including the service file and environment file
		:return:
		"""
		super().remove_service()

		# Remove the socket file if it exists
		if self.socket and os.path.exists(self.socket):
			try:
				os.remove(self.socket)
			except Exception as e:
				logger.error('Error removing socket file %s: %s' % (self.socket, str(e)))

		# Remove the systemd socket file
		socket_path = os.path.join('/etc/systemd/system', os.path.basename(self.socket))
		if os.path.exists(socket_path):
			try:
				os.remove(socket_path)
			except Exception as e:
				logger.error('Error removing systemd socket file %s: %s' % (socket_path, str(e)))

		self.reload()
