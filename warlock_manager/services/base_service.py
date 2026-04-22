import datetime
import logging
import os
import shutil
import sys
import time
from abc import abstractmethod, ABC
from zipfile import ZipFile
from SystemdUnitParser import SystemdUnitParser

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from warlock_manager.mods.base_mod import BaseMod

from warlock_manager.apps.base_app import BaseApp
from warlock_manager.libs.get_wan_ip import get_wan_ip
from warlock_manager.libs.tui import prompt_yn, prompt_text
from warlock_manager.libs.cmd import Cmd, BackgroundCmd
from warlock_manager.libs.ports import get_listening_port
from warlock_manager.libs.firewall import Firewall
from warlock_manager.libs import utils


class BaseService(ABC):
	"""
	Service definition and handler
	"""
	def __init__(self, service: str, game: BaseApp):
		"""
		Initialize and load the service definition

		:param service: The name of the systemd service to manage
		:param game: The game app instance this service belongs to
		"""

		self.service = service
		"""
		:type str:
		Name of the service, must match the systemd service name for this instance

		example: `/etc/systemd/system/minecraft.service` would be `minecraft`
		"""

		self._service_file = '/etc/systemd/system/%s.service' % service
		"""
		:type str:
		Full path to the systemd service file for this service,
		used for checking existence and loading configuration options from the file
		"""

		self._env_file = os.path.join(utils.get_base_directory(), 'Environments', '%s.env' % service)
		"""
		:type str:
		Fully resolved path on the filesystem for the environmental variable for this service
		"""

		self.game = game
		"""
		:type BaseApp:
		Game application instance this service belongs to,
		used for accessing game-level configuration and APIs
		"""

		self.desc = '%s (%s)' % (game.desc, service)
		"""
		:type str:
		Short descriptor for this game instance, used in systemd
		"""

		self.configured = False
		"""
		:type bool:
		Set to True after configuration files have been loaded successfully,
		used to prevent saving configs before they're loaded
		"""

		self.configs = {}
		"""
		:type dict:
		Key-value pair of configuration file instances for this service

		Each service should have its own key with the value being the ConfigHandler for that appropriate type.
		"""

	def load(self):
		"""
		Load the configuration files

		:return:
		"""
		for config in self.configs.values():
			if config.exists():
				config.load()
				self.configured = True
			elif config.path:
				# Doesn't exist, (that's fine),
				# but the directory structure should be available to make it more simple for saving
				self.game.ensure_file_parent_exists(config.path)

	def get_options(self) -> list:
		"""
		Get a list of available configuration options for this service

		:return:
		"""
		opts = []
		for config in self.configs.values():
			opts.extend(list(config.options.keys()))

		# Sort alphabetically
		opts.sort()

		return opts

	def get_option_value(self, option: str) -> str | int | bool:
		"""
		Get a configuration option from the service config

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_value(option)

		logging.warning('Invalid option: %s, not present in service configuration!' % option)
		return ''

	def get_option_default(self, option: str) -> str:
		"""
		Get the default value of a configuration option

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_default(option)

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return ''

	def get_option_type(self, option: str) -> str:
		"""
		Get the type of configuration option from the service config

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_type(option)

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return ''

	def get_option_help(self, option: str) -> str:
		"""
		Get the help text of a configuration option from the service config

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.options[option].help

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return ''

	def option_value_updated(self, option: str, previous_value, new_value) -> bool | None:
		"""
		Handle any special actions needed when an option value is updated

		:param option:
		:param previous_value:
		:param new_value:
		:return:
		"""
		pass

	def get_option_group(self, option: str):
		"""
		Get the display group for a configuration option
		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.options[option].group

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return 'Options'

	def set_option(self, option: str, value: str | int | bool) -> bool:
		"""
		Set a configuration option in the service config

		:param option:
		:param value:
		:return:
		"""
		for config in self.configs.values():
			opt = config.get_config(option)
			if opt is not None:
				# Convert input value to a _system_ value to ensure '0' matches False
				new_value = opt.to_system_type(value)
				previous_value = config.get_value(option)
				if previous_value == new_value and config.has_value(option):
					# No change
					return True

				config.set_value(option, value)
				config.save()

				# Allow the extending service to handle any special actions needed for this option update
				post_result = self.option_value_updated(option, previous_value, new_value)
				if post_result is True:
					# Post-update either returned a successful operation or nothing at all, either is fine.
					logging.info('Updated option %s to %s and ran post-update actions successfully' % (option, value))
					return True
				elif post_result is None:
					logging.debug('Post-update returned None, this is fine as it indicates no post-actions taken')
					logging.info('Updated option %s to %s' % (option, value))
					return True
				else:
					# Post-update explictly returned False, this indicates a problem occurred.
					logging.warning('Configuration saved, but unable to complete post-update actions!')
					return False

		logging.warning('Invalid option: %s, not present in service configuration!' % option)
		return False

	def option_has_value(self, option: str) -> bool:
		"""
		Check if a configuration option has a value set in the service config

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.has_value(option)

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return False

	def get_option_options(self, option: str):
		"""
		Get the list of possible options for a configuration option

		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_options(option)

		print('Invalid option: %s, not present in service configuration!' % option, file=sys.stderr)
		return []

	def option_ensure_set(self, option: str):
		"""
		Ensure that a configuration option has a value set, using the default if not

		:param option:
		:return:
		"""
		if not self.option_has_value(option):
			default = self.get_option_default(option)
			self.set_option(option, default)

	def get_name(self) -> str:
		"""
		Get the display name of this service

		:return:
		"""
		return self.service

	def get_ip(self) -> str:
		"""
		Get the IP to connect to, can also be a hostname if necessary.

		By default it just returns the WAN IP of the server.
		:return:
		"""
		return get_wan_ip()

	def get_port(self) -> int | None:
		"""
		Get the primary port of the service, or None if not applicable

		:return:
		"""
		return None

	def get_port_protocol(self) -> str | None:
		"""
		Get if the primary port of this service is UDP or TCP.

		(Most games use UDP, but override this to change it)

		:return:
		"""
		return 'UDP'

	def prompt_option(self, option: str):
		"""
		Prompt the user to set a configuration option for the service

		:param option:
		:return:
		"""
		val_type = self.get_option_type(option)
		val = self.get_option_value(option)
		help_text = self.get_option_help(option)

		print('')
		if help_text:
			print(help_text)
		if val_type == 'bool':
			default = 'y' if val else 'n'
			val = prompt_yn('%s: ' % option, default)
		else:
			val = prompt_text('%s: ' % option, default=val, prefill=True)

		self.set_option(option, val)

	def get_player_max(self) -> int | None:
		"""
		Get the maximum player count on the server, or None if the API is unavailable

		:return:
		"""
		return None

	def get_player_count(self) -> int | None:
		"""
		Get the current player count on the server, or None if the API is unavailable

		:return:
		"""
		players = self.get_players()
		if players is not None:
			return len(players)
		else:
			return None

	def get_players(self) -> list | None:
		"""
		Get a list of current players on the server, or None if the API is unavailable

		:return:
		"""
		return None

	def get_pid(self) -> int:
		"""
		Get the PID of the running service, or 0 if not running

		:return:
		"""
		check = Cmd(['systemctl', 'show', '-p', 'MainPID', self.service])
		check.is_memory_cacheable(3)
		pid = check.text[8:]
		return int(pid)

	def get_process_status(self) -> int:
		"""
		Get the exit status of the main process of the service, or 0 if running successfully

		:return:
		"""
		code = Cmd(['systemctl', 'show', '-p', 'ExecMainStatus', self.service]).text[15:]
		return -1 if code == '' else int(code)

	@abstractmethod
	def get_game_pid(self) -> int:
		"""
		Get the primary game process PID of the actual game server, or 0 if not running

		:return:
		"""
		...

	def get_memory_usage(self) -> str:
		"""
		Get the formatted memory usage of the service, or N/A if not running

		Returns "# GB" or "# MB" depending on the amount of memory used,
		or "N/A" if the memory usage cannot be determined (service not running, etc)

		:return:
		"""

		pid = self.get_game_pid()

		if pid == 0 or pid is None:
			return 'N/A'

		mem = Cmd(['ps', 'h', '-p', str(pid), '-o', 'rss']).text

		if mem.isdigit():
			mem = int(mem)
			if mem >= 1024 * 1024:
				mem_gb = mem / (1024 * 1024)
				return '%.2f GB' % mem_gb
			else:
				mem_mb = mem // 1024
				return '%.0f MB' % mem_mb
		else:
			return 'N/A'

	def get_cpu_usage(self) -> str:
		"""
		Get the formatted CPU usage of the service, or N/A if not running

		Returns "#%" of CPU used, or "N/A" if the CPU usage cannot be determined (service not running, etc)

		:return:
		"""

		pid = self.get_game_pid()

		if pid == 0 or pid is None:
			return 'N/A'

		cpu = Cmd(['ps', 'h', '-p', str(pid), '-o', '%cpu']).text

		if cpu.replace('.', '', 1).isdigit():
			return '%.0f%%' % float(cpu)
		else:
			return 'N/A'

	def get_exec_start_status(self) -> dict | None:
		"""
		Get the ExecStart status of the service

		This includes:

		* path - string: Path of the ExecStartPre command
		* arguments - string: Arguments passed to the ExecStartPre command
		* start_time - datetime: Time the ExecStartPre command started
		* stop_time - datetime: Time the ExecStartPre command stopped
		* pid - int: PID of the ExecStartPre command
		* code - string: Exit code of the ExecStartPre command
		* status - int: Exit status of the ExecStartPre command
		* runtime - int: Runtime of the ExecStartPre command in seconds

		:return:
		"""
		return self._get_exec_status('ExecStart')

	def get_exec_start_pre_status(self) -> dict | None:
		"""
		Get the ExecStart status of the service

		This includes:

		* path - string: Path of the ExecStartPre command
		* arguments - string: Arguments passed to the ExecStartPre command
		* start_time - datetime: Time the ExecStartPre command started
		* stop_time - datetime: Time the ExecStartPre command stopped
		* pid - int: PID of the ExecStartPre command
		* code - string: Exit code of the ExecStartPre command
		* status - int: Exit status of the ExecStartPre command
		* runtime - int: Runtime of the ExecStartPre command in seconds

		:return:
		"""
		return self._get_exec_status('ExecStartPre')

	def _get_exec_status(self, lookup: str) -> dict | None:
		"""
		Get the ExecStartPre status of the service

		This includes:

		* path - string: Path of the ExecStartPre command
		* arguments - string: Arguments passed to the ExecStartPre command
		* start_time - datetime: Time the ExecStartPre command started
		* stop_time - datetime: Time the ExecStartPre command stopped
		* pid - int: PID of the ExecStartPre command
		* code - string: Exit code of the ExecStartPre command
		* status - int: Exit status of the ExecStartPre command
		* runtime - int: Runtime of the ExecStartPre command in seconds

		:return:
		"""

		output = Cmd(['systemctl', 'show', '-p', lookup, self.service]).text[len(lookup) + 1:]
		if output == '':
			return None

		output = output[1:-1]  # Remove surrounding {}
		parts = output.split(' ; ')
		result = {}
		for part in parts:
			if '=' not in part:
				continue
			key, val = part.split('=', 1)
			key = key.strip()
			val = val.strip()
			if key == 'path':
				result['path'] = val
			elif key == 'argv[]':
				result['arguments'] = val
			elif key == 'start_time':
				val = val[1:-1]  # Remove surrounding []
				if val == 'n/a':
					result['start_time'] = None
				else:
					result['start_time'] = datetime.datetime.strptime(val, '%a %Y-%m-%d %H:%M:%S %Z')
			elif key == 'stop_time':
				val = val[1:-1]
				if val == 'n/a':
					result['stop_time'] = None
				else:
					result['stop_time'] = datetime.datetime.strptime(val, '%a %Y-%m-%d %H:%M:%S %Z')
			elif key == 'pid':
				result['pid'] = int(val)
			elif key == 'code':
				if val == '(null)':
					result['code'] = None
				else:
					result['code'] = val
			elif key == 'status':
				if '/' in val:
					result['status'] = int(val.split('/')[0])
				else:
					result['status'] = int(val)

		if result['start_time'] and result['stop_time']:
			delta = result['stop_time'] - result['start_time']
			result['runtime'] = int(delta.total_seconds())
		else:
			result['runtime'] = 0

		return result

	def _is_enabled(self) -> str:
		"""
		Get the output of systemctl is-enabled for this service

		Returns:

		* enabled - Service is enabled
		* disabled - Service is disabled
		* static - Service is static and cannot be enabled/disabled
		* masked - Service is masked

		:return:
		"""
		return Cmd(['systemctl', 'is-enabled', self.service]).text

	def _is_active(self) -> str:
		"""
		Returns a string based on the status of the service:

		Returns:

		* active - Running
		* reloading - Running but reloading configuration
		* inactive - Stopped
		* failed - Failed to start
		* activating - Starting
		* deactivating - Stopping

		:return:
		"""
		check = Cmd(['systemctl', 'is-active', self.service])
		check.is_memory_cacheable(3)
		return check.text

	def is_enabled(self) -> bool:
		"""
		Check if this service is enabled in systemd

		:return:
		"""
		return self._is_enabled() == 'enabled'

	def is_running(self) -> bool:
		"""
		Check if this service is currently running

		:return:
		"""
		return self._is_active() == 'active'

	def is_starting(self) -> bool:
		"""
		Check if this service is currently starting

		:return:
		"""
		return self._is_active() == 'activating'

	def is_stopping(self) -> bool:
		"""
		Check if this service is currently stopping

		:return:
		"""
		return self._is_active() == 'deactivating'

	def is_stopped(self) -> bool:
		"""
		Check if this service is currently stopped

		:return:
		"""
		status = self._is_active()
		return status == 'inactive' or status == 'failed'

	def is_api_enabled(self) -> bool:
		"""
		Check if an API is available for this service

		:return:
		"""
		return False

	def is_port_open(self) -> bool:
		"""
		Check if all required ports for this game are open

		:return:
		"""
		for ports in self.get_port_definitions():
			if len(ports) >= 4:
				# Check if this port is optional; if so we don't care about it.
				if ports[3]:
					continue
			if isinstance(ports[0], int):
				check_port = ports[0]
			else:
				check_port = self.get_option_value(ports[0])

			check_protocol = ports[1]

			if get_listening_port(check_port, check_protocol) is None:
				return False

		# All ports are open
		return True

	def enable(self):
		"""
		Enable this service in systemd

		:return:
		"""
		if os.geteuid() != 0:
			print('ERROR - Unable to enable game service unless run with sudo', file=sys.stderr)
			return
		Cmd(['systemctl', 'enable', self.service]).run()

	def disable(self):
		"""
		Disable this service in systemd

		:return:
		"""
		if os.geteuid() != 0:
			print('ERROR - Unable to disable game service unless run with sudo', file=sys.stderr)
			return
		Cmd(['systemctl', 'disable', self.service]).run()

	def print_logs(self, lines: int = 20):
		"""
		Print the latest logs from this service

		:param lines:
		:return:
		"""
		print(self.get_logs(lines))

	def get_logs(self, lines: int = 20) -> str:
		"""
		Get the latest logs from this service

		:param lines:
		:return:
		"""
		return Cmd(['journalctl', '-qu', self.service, '-n', str(lines), '--no-pager']).text

	def send_message(self, message: str):
		"""
		Send a message to all players via the game API

		:param message:
		:return:
		"""
		pass

	def save_world(self):
		"""
		Force a world save via the game API

		:return:
		"""
		pass

	@abstractmethod
	def get_port_definitions(self) -> list:
		"""
		Get a list of port definitions for this service

		Each entry in the returned list should contain 3 items:

		* Config name or integer of port (for non-definable ports)
		* 'UDP' or 'TCP' to indicate protocol
		* Short description of the port purpose
		* Optional boolean to indicate if this is an optional port (ie: not checked at startup)

		Example:

		```python
		return [
			['Game Port', 'UDP', 'Primary game port for clients to connect to', False],
			[25565, 'TCP', 'RCON port, statically assigned and cannot be changed', True]
		]
		```

		:return:
		"""
		...

	def get_ports(self) -> list:
		"""
		Get the list of all ports used by this game, (at least that are registered)
		and their status

		Each port in the returned list is expected to contain the following properties:

		* port - Port number
		* protocol - UDP or TCP to indicate the port protocol
		* description - Short description of the port function
		* global - T/F if this port listens globally
		* listening - T/F if this port is currently open (listening)
		* owned - T/F if this port is owned by this process
		* open - T/F if this port is currently open in the firewall to default
		* option - Option name that controls this port setting, or None if static

		:return:
		"""
		ret = []
		game_pid = self.get_game_pid()
		pid = self.get_pid()

		for port_def in self.get_port_definitions():
			if isinstance(port_def[0], int):
				port = port_def[0]
				configuration = None
			else:
				port = self.get_option_value(port_def[0])
				configuration = port_def[0]

			protocol = port_def[1]
			description = port_def[2]

			listening_status = get_listening_port(port, protocol)
			if listening_status is not None:
				is_global = listening_status['ip'] != '127.0.0.1'
				is_listening = True
				is_owned = listening_status['pid'] in (game_pid, pid)
				is_open = Firewall.is_global_open(port, protocol)
			else:
				is_global = False
				is_listening = False
				is_owned = False
				is_open = Firewall.is_global_open(port, protocol)

			ret.append({
				'port': port,
				'protocol': protocol,
				'description': description,
				'global': is_global,
				'listening': is_listening,
				'owned': is_owned,
				'open': is_open,
				'option': configuration,
			})

		return ret

	def start(self):
		"""
		Start this service in systemd

		:return:
		"""
		if self.is_running():
			logging.warning('Game is already running!')
			return

		if self.is_starting():
			logging.warning('Game is currently starting!')
			return

		if os.geteuid() != 0:
			logging.error('Unable to start game service unless run with sudo')
			return

		logging.info('Starting game via systemd, this may take a minute...')
		BackgroundCmd(['systemctl', 'start', self.service]).run()

	def pre_stop(self) -> bool:
		"""
		Perform operations necessary for safely stopping a server

		Called automatically via systemd
		:return:
		"""
		# Send a message to Discord that the instance is stopping
		msg = self.game.get_option_value('Instance Stopping (Discord)')
		if msg != '':
			if '{instance}' in msg:
				msg = msg.replace('{instance}', self.get_name())
			self.game.send_discord_message(msg)

		# Send message to players in-game that the server is shutting down,
		# (only if the API is available)
		if self.is_api_enabled():
			timers = (
				(self.game.get_option_value('Shutdown Warning 5 Minutes'), 60),
				(self.game.get_option_value('Shutdown Warning 4 Minutes'), 60),
				(self.game.get_option_value('Shutdown Warning 3 Minutes'), 60),
				(self.game.get_option_value('Shutdown Warning 2 Minutes'), 60),
				(self.game.get_option_value('Shutdown Warning 1 Minute'), 30),
				(self.game.get_option_value('Shutdown Warning 30 Seconds'), 30),
				(self.game.get_option_value('Shutdown Warning NOW'), 0),
			)
			for timer in timers:
				players = self.get_player_count()
				if players is not None and players > 0:
					print('Players are online, sending warning message: %s' % timer[0])
					self.send_message(timer[0])
					if timer[1]:
						time.sleep(timer[1])
				else:
					break

		# Force a world save before stopping, if the API is available
		if self.is_api_enabled():
			print('Forcing server save')
			self.save_world()
			time.sleep(5)

		return True

	def post_start(self) -> bool:
		"""
		Perform the necessary operations for after a game has started

		:return:
		"""
		logging.info('Waiting for game to become available for start confirmation...')
		start_timer = time.time()
		seconds_elapsed = round(time.time() - start_timer)
		ready = False
		socket_ready = False
		max_wait = 300
		max_wait_minutes = str(max_wait // 60)
		max_wait_seconds = max_wait % 60
		if max_wait_seconds < 10:
			max_wait_seconds = '0' + str(max_wait_seconds)
		else:
			max_wait_seconds = str(max_wait_seconds)

		while not ready and seconds_elapsed < max_wait:
			seconds_elapsed = round(time.time() - start_timer)
			since_minutes = str(seconds_elapsed // 60)
			since_seconds = seconds_elapsed % 60
			if since_seconds < 10:
				since_seconds = '0' + str(since_seconds)
			else:
				since_seconds = str(since_seconds)

			logging.info(
				'Waiting (%s:%s / %s:%s max wait)' %
				(since_minutes, since_seconds, max_wait_minutes, max_wait_seconds)
			)
			time.sleep(15)

			# Base checks; the process should still be running
			if self.get_process_status() != 0:
				logging.error('Game crashed during startup!')
				return False

			if self.get_pid() == 0:
				logging.error('Game failed to start or no PID found.')
				return False

			if not socket_ready:
				# Pull the socket information to know if the game is running yet
				# If it's None, that means this information won't be available and we can skip the check.
				port_open = self.is_port_open()
				if port_open is None:
					logging.info('Unable to determine if port is open, skipping check.')
					socket_ready = True
				elif port_open is True:
					socket_ready = True
					logging.info('Game port is open, continuing to API check')
				else:
					logging.info('Game port is closed, waiting for it to open.')
					continue

			if self.is_api_enabled():
				players = self.get_player_count()
				if players is not None:
					logging.info('API connected!')
					ready = True
			else:
				logging.info('API is not available, skipping start confirmation.')
				ready = True

		if ready:
			# Perform all operations required for a successful, confirmed startup
			msg = self.game.get_option_value('Instance Started (Discord)')
			if msg != '':
				if '{instance}' in msg:
					msg = msg.replace('{instance}', self.get_name())
				self.game.send_discord_message(msg)
		else:
			# Checks failed to complete within allowed time.
			# This does not mean the game didn't start, it just didn't start _within allocated time_.
			logging.warning('API did not respond within the allowed time!')

		return True

	def _delayed_action(self, action):
		"""
		If players are logged in, send 5-minute notifications for an hour before stopping the server

		:param action:
		:return:
		"""

		if action not in ['stop', 'restart', 'update']:
			print('ERROR - Invalid action for delayed action: %s' % action, file=sys.stderr)
			return

		if os.geteuid() != 0:
			print('ERROR - Unable to stop game service unless run with sudo', file=sys.stderr)
			return

		start = round(time.time())
		msg = self.game.get_option_value('%s_delayed' % action)
		if msg == '':
			msg = 'Server will %s in {time} minutes. Please prepare to log off safely.' % action

		print(
			'Issuing %s for %s, please wait as this will give players up to an hour to log off safely.' %
			(action, self.service)
		)

		while True:
			minutes_left = 55 - ((round(time.time()) - start) // 60)
			player_count = self.get_player_count()

			if player_count == 0 or player_count is None:
				# No players online, stop the timer
				break

			if '{time}' in msg:
				msg = msg.replace('{time}', str(minutes_left))

			if minutes_left <= 5:
				# Once the timer hits 5 minutes left, drop to the standard stop procedure.
				break

			if minutes_left % 5 == 0:
				self.send_message(msg)

			if minutes_left % 5 == 0 and minutes_left > 5:
				print('%s minutes remaining before %s.' % (str(minutes_left), action))

			time.sleep(60)

		if action == 'stop':
			self.stop()
		elif action == 'update':
			is_running = self.is_running()
			if is_running:
				self.stop()
			# Stop may take 5 more minutes to complete.
			counter = 0
			while counter <= 10:
				if not self.is_running():
					break
				counter += 1
				time.sleep(30)
			self.update()
			# Should it start back up?
			if is_running:
				self.start()
		else:
			self.restart()

	def stop(self):
		"""
		Stop this service in systemd

		:return:
		"""
		if os.geteuid() != 0:
			print('ERROR - Unable to stop game service unless run with sudo', file=sys.stderr)
			return

		print('Stopping server, please wait...')
		BackgroundCmd(['systemctl', 'stop', self.service]).run()

	def delayed_stop(self):
		"""
		Delayed stop procedure for this service

		:return:
		"""
		self._delayed_action('stop')

	def restart(self):
		"""
		Restart this service in systemd

		:return:
		"""
		if not self.is_running():
			print('%s is not currently running!' % self.service, file=sys.stderr)
			return

		self.stop()
		self.start()

	def delayed_restart(self):
		"""
		Delayed restart procedure for this service

		:return:
		"""
		self._delayed_action('restart')

	def reload(self):
		"""
		Reload systemd unit files to pick up changes to service configurations.
		:return:
		"""
		if os.geteuid() != 0:
			print('ERROR - Unable to stop game service unless run with sudo', file=sys.stderr)
			return

		Cmd(['systemctl', 'daemon-reload']).run()

	def check_update_available(self) -> bool:
		"""
		Check if there's an update available for this game

		:return:
		"""
		return False

	def update(self) -> bool:
		"""
		Update the game server

		:return:
		"""
		return False

	def delayed_update(self):
		"""
		Perform a delayed update of the game, giving players time to log off safely before restarting the server.

		Provides a 1-hour warning with 5-minute notifications, then updates the game and restarts all services.
		This is intended to be used when performing maintenance or updates that require downtime,
		but you want to give players a chance to log off safely before the server goes down.

		:return:
		"""
		if not self.game.multi_binary:
			print('ERROR - This game does not support updating instances separately.', file=sys.stderr)
		else:
			self._delayed_action('update')

	def post_update(self):
		"""
		Perform any post-update actions needed for this game

		Called immediately after an update is performed but before services are restarted.

		:return:
		"""
		pass

	def cmd(self, cmd: str) -> None | str:
		"""
		Send a command to the game server via the API, if available

		:param cmd:
		:return: None if the API is not available, or the result of the command
		"""
		print('This service does not have an API available to send commands.', file=sys.stderr)
		return None

	def get_commands(self) -> None | list[str]:
		"""
		Get a list of available commands for this service

		:return:
		"""
		return None

	def get_systemd_config(self) -> SystemdUnitParser:
		"""
		Get the systemd unit configuration for this service, if available
		:return:
		"""
		config = SystemdUnitParser()
		if os.path.exists(self._service_file):
			config.read(self._service_file)

		# Load default sections that are required
		if 'Unit' not in config:
			config['Unit'] = {}
		if 'Service' not in config:
			config['Service'] = {}
		if 'Install' not in config:
			config['Install'] = {}

		# Calculate the working directory of this game service,
		# If the game is registered as a multi-binary game, each service is contained within its own directory,
		# otherwise all instances share AppFiles.
		working_directory = self.get_app_directory()

		# Populate the configuration with this environment
		config['Unit']['Description'] = self.desc
		config['Unit']['After'] = 'network.target'
		config['Service']['Type'] = 'simple'
		config['Service']['LimitNOFILE'] = '1000000'
		config['Service']['User'] = str(utils.get_app_uid())
		config['Service']['Group'] = str(utils.get_app_gid())
		config['Service']['WorkingDirectory'] = working_directory
		config['Service']['EnvironmentFile'] = self._env_file
		config['Service']['ExecStart'] = self.get_executable()
		config['Service']['ExecStop'] = '%s pre-stop --service %s' % (os.path.realpath(sys.argv[0]), self.service)
		config['Service']['ExecStartPost'] = '%s post-start --service %s' % (os.path.realpath(sys.argv[0]), self.service)
		config['Service']['Restart'] = 'on-failure'
		config['Service']['RestartSec'] = '1800s'
		config['Service']['TimeoutStartSec'] = '600s'
		config['Install']['WantedBy'] = 'multi-user.target'
		return config

	def get_app_directory(self) -> str:
		"""
		Get the working directory for this game service, which is the directory that contains the game files and executable

		If the game is registered as a multi-binary game, each service is contained within its own directory,
		otherwise all instances share AppFiles.

		:return:
		"""
		base = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'AppFiles')
		if self.game.multi_binary:
			base = os.path.join(base, self.service)

		return base

	def get_save_directory(self) -> str:
		"""
		Get the parent directory that contains the Save files for this game

		By default this is just the app directory (AppFiles or AppFiles/{servicename}),
		but this can be changed if the game saves files outside this directory.

		:return:
		"""
		return self.get_app_directory()

	def get_backup_directory(self) -> str:
		"""
		Get the backup directory for this game service, which is the directory that contains backups of the game files

		All game services are contained in their own separate directory to make management easier.

		:return:
		"""
		base = os.path.join(
			os.path.dirname(os.path.realpath(sys.argv[0])),
			'Backups',
			self.service
		)

		return base

	def get_environment(self) -> dict:
		"""
		Get the environment variables for this service as a dictionary

		:return:
		"""
		return {
			'XDG_RUNTIME_DIR': '/run/user/%s' % self.game.get_app_uid(),
		}

	def get_info(self) -> dict:
		"""
		Get a dictionary of information about this service for display in the TUI

		This is used by Warlock to retrieve information about a given service.
		:return:
		"""
		return {
			# Service-related fields
			'service': self.service,
			'name': self.get_name(),
			'ip': self.get_ip(),
			'port': self.get_port(),
			'enabled': self.is_enabled(),
			'max_players': self.get_player_max(),
			# API-related fields
			'app_dir': self.get_app_directory(),
			'bak_dir': self.get_backup_directory(),
			'version': self.get_version(),
			'loader': self.get_loader(),
		}

	def build_environment_file(self):
		"""
		Build the environment file for this service

		:return:
		"""
		with open(self._env_file, 'w') as f:
			env = self.get_environment()
			for key in env:
				f.write('%s=%s\n' % (key, env[key]))
		self.game.ensure_file_ownership(self._env_file)

	def build_systemd_config(self):
		"""
		Build and save the systemd service file for this service

		WILL OVERWRITE ANY EXISTING SERVICE FILE WITHOUT PROMPT, USE WITH CAUTION
		:return:
		"""
		config = self.get_systemd_config()
		with open(self._service_file, 'w') as f:
			config.write(f)

	def create_service(self):
		"""
		Create the systemd service for this game, including the service file and environment file
		:return:
		"""

		# Build the systemd service file for this service
		self.build_systemd_config()
		logging.info('Created systemd service file for %s at %s' % (self.service, self._service_file))

		# Save the environmental variable file for this service
		self.build_environment_file()
		logging.info('Created environment file for %s at %s' % (self.service, self._env_file))

		# Grab the ports from this service and try to automatically update them to the next available port
		# NOTICE, this will only check against services within this same game,
		# so multiple games on the same server may need adjusted manually.
		port_configs = self.get_port_definitions()
		for port_config in port_configs:
			if isinstance(port_config[0], int):
				# This is a static port, skip it
				continue

			port = self.get_option_value(port_config[0])
			port_default = self.get_option_default(port_config[0])
			if port == 0:
				# This port does not have a default value, probably not enabled by default.
				continue
			new_port = self.game.get_next_available_port(self, port, port_config[1])

			if port_default == new_port:
				# New installations where the default port may not trigger the 'change' logic
				# as the port _technically_ didn't change, therefore the firewall rules won't be added.
				logging.info('Setting %s to 0 to force firewall change' % port_config[0])
				self.set_option(port_config[0], 0)

			self.set_option(port_config[0], new_port)
			if new_port != port:
				logging.info('Set %s to %s to try to avoid conflicts' % (port_config[0], new_port))
			else:
				logging.info('Set %s to %s' % (port_config[0], new_port))

		# Reload systemd to pick up the new service
		self.reload()

		# Ensure the target directory for this service exists and has the correct ownership
		target_dir = self.get_app_directory()
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)
			logging.info('Created app directory for %s at %s' % (self.service, target_dir))
			self.game.ensure_file_ownership(target_dir)

	def remove_service(self):
		"""
		Remove the systemd service for this game, including the service file and environment file
		:return:
		"""

		# Stop / disable this service in systemd
		self.stop()
		self.disable()

		if os.path.exists(self._service_file):
			os.remove(self._service_file)
			logging.info('Removed systemd service file for %s at %s' % (self.service, self._service_file))

		if os.path.exists(self._env_file):
			os.remove(self._env_file)
			logging.info('Removed environment file for %s at %s' % (self.service, self._env_file))

		target_dir = self.get_app_directory()
		app_dir = os.path.join(utils.get_base_directory(), 'AppFiles')
		if target_dir != app_dir and os.path.exists(target_dir):
			# Only remove app directory if it's different than the game app.
			# This is important because by default game instances share the same application base.
			if not target_dir.startswith(app_dir):
				raise Exception('Attempting to remove an application directory that is outside the scope of the game!')

			shutil.rmtree(target_dir)
			logging.info('Removed app directory for %s at %s' % (self.service, target_dir))

		for config in self.configs.values():
			if config.path and os.path.exists(config.path):
				os.remove(config.path)
				logging.info('Removed config file for %s at %s' % (self.service, config.path))

		self.reload()

	@abstractmethod
	def get_executable(self) -> str:
		"""
		Get the full executable for this game service
		:return:
		"""
		...

	def get_save_files(self) -> list | None:
		"""
		Get the list of supplemental files or directories for this game, or None if not applicable

		This list of files **should not** be fully resolved, and will use `self.get_app_directory()` as the base path.
		For example, to return `AppFiles/SaveData` and `AppFiles/Config`:

		```python
		return ['SaveData', 'Config']
		```

		:return:
		"""
		return None

	def backup(self, max_backups: int = 0) -> bool:
		"""
		Perform a backup of the game configuration and save files

		:param max_backups: Maximum number of backups to keep (0 = unlimited)
		:return:
		"""
		self.prepare_backup()
		backup_path = self.complete_backup(max_backups)
		print('Backup saved to %s' % backup_path)
		return True

	def prepare_backup(self) -> str:
		"""
		Prepare a backup directory for this game and return the file path

		:return:
		"""
		base = utils.get_base_directory()
		temp_store = os.path.join(base, '.save-%s' % self.service)
		save_source = self.get_save_directory()
		save_files = self.get_save_files()

		# Temporary directories for various file sources
		for d in ['config', 'save']:
			p = os.path.join(temp_store, d)
			if not os.path.exists(p):
				os.makedirs(p)

		# Copy the various configuration files used by the game
		for cfg in self.configs.values():
			src = cfg.path
			if src and os.path.exists(src):
				print('Backing up configuration file: %s' % src)
				dst = os.path.join(temp_store, 'config', os.path.basename(src))
				shutil.copy(src, dst)

		# Copy save files if specified
		if save_source and save_files:
			for f in save_files:
				src = os.path.join(save_source, f)
				dst = os.path.join(temp_store, 'save', f)
				if os.path.exists(src):
					if os.path.isfile(src):
						print('Backing up save file: %s' % src)
						if not os.path.exists(os.path.dirname(dst)):
							os.makedirs(os.path.dirname(dst))
						shutil.copy(src, dst)
					else:
						print('Backing up save directory: %s' % src)
						if not os.path.exists(dst):
							os.makedirs(dst)
						shutil.copytree(src, dst, dirs_exist_ok=True)
				else:
					print('Save file %s does not exist, skipping...' % src, file=sys.stderr)

		# Save the environment file for this service, if one is set
		if self._env_file:
			src = self._env_file
			if os.path.exists(src):
				print('Backing up environment file: %s' % src)
				dst = os.path.join(temp_store, 'environment')
				shutil.copy(src, dst)

		return temp_store

	def complete_backup(self, max_backups: int = 0) -> str:
		"""
		Complete the backup process by creating the final archive and cleaning up temporary files

		:return:
		"""
		base = utils.get_base_directory()
		temp_store = os.path.join(base, '.save-%s' % self.service)
		target_dir = self.get_backup_directory()
		base_name = self.service
		# Ensure no invalid characters in the name
		replacements = {
			'/': '_',
			'\\': '_',
			':': '',
			'*': '',
			'?': '',
			'"': '',
			"'": '',
			' ': '_'
		}
		for old, new in replacements.items():
			base_name = base_name.replace(old, new)

		# Ensure the target directory exists; this will store the finalized backups
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)
			self.game.ensure_file_ownership(target_dir)

		# Create the final archive
		timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
		backup_name = '%s-backup-%s.tar.gz' % (base_name, timestamp)
		backup_path = os.path.join(target_dir, backup_name)
		print('Creating backup archive: %s' % backup_path)
		shutil.make_archive(backup_path[:-7], 'gztar', temp_store)

		# Ensure consistent ownership
		self.game.ensure_file_ownership(backup_path)

		# Cleanup
		shutil.rmtree(temp_store)

		# Remove old backups if necessary
		if max_backups > 0:
			backups = []
			for f in os.listdir(target_dir):
				if f.startswith('%s-backup-' % base_name) and f.endswith('.tar.gz'):
					full_path = os.path.join(target_dir, f)
					backups.append((full_path, os.path.getmtime(full_path)))
			backups.sort(key=lambda x: x[1])  # Sort by modification time
			while len(backups) > max_backups:
				old_backup = backups.pop(0)
				os.remove(old_backup[0])
				print('Removed old backup: %s' % old_backup[0])

		return backup_path

	def restore(self, path: str) -> bool:
		"""
		Restore a backup from the given filename

		:param path:
		:return:
		"""
		temp_store = self.prepare_restore(path)
		if temp_store is False:
			return False
		self.complete_restore()
		return True

	def prepare_restore(self, filename) -> str | bool:
		"""
		Prepare to restore a backup by extracting it to a temporary location

		:param filename:
		:return:
		"""
		if not os.path.exists(filename):
			# Check if the file exists in the designated Backups directory for this service
			backup_path = os.path.join(self.get_backup_directory(), filename)
			if os.path.exists(backup_path):
				filename = backup_path
			else:
				print('Backup file %s does not exist, cannot continue!' % filename, file=sys.stderr)
				return False

		if self.is_running():
			print('Game server is currently running, please stop it before restoring a backup!', file=sys.stderr)
			return False

		base = utils.get_base_directory()
		temp_store = os.path.join(base, '.restore-%s' % self.service)
		save_dest = self.get_save_directory()

		os.makedirs(temp_store, exist_ok=True)

		# Extract the archive to the temporary location
		print('Extracting backup archive: %s' % filename)
		shutil.unpack_archive(filename, temp_store)

		# Copy the various configuration files used by the game
		for cfg in self.configs.values():
			dst = cfg.path
			if dst:
				src = os.path.join(temp_store, 'config', os.path.basename(dst))
				if os.path.exists(src):
					print('Restoring configuration file: %s' % dst)
					shutil.copy(src, dst)
					self.game.ensure_file_ownership(dst)

		# If the save destination is specified, perform those files/directories too.
		if save_dest:
			save_src = os.path.join(temp_store, 'save')
			if os.path.exists(save_src):
				for item in os.listdir(save_src):
					src = os.path.join(save_src, item)
					dst = os.path.join(save_dest, item)
					print('Restoring save file: %s' % dst)
					if os.path.isfile(src):
						shutil.copy(src, dst)
					else:
						shutil.copytree(src, dst, dirs_exist_ok=True)
					self.game.ensure_file_ownership(dst)

		# Restore the environment file for this service, if one is set
		if self._env_file:
			dst = self._env_file
			save_src = os.path.join(temp_store, 'environment')
			if os.path.exists(save_src):
				print('Restoring environment file: %s' % dst)
				shutil.copy(save_src, dst)

		return temp_store

	def complete_restore(self):
		"""
		Complete the restore process by cleaning up temporary files

		:return:
		"""
		base = utils.get_base_directory()
		temp_store = os.path.join(base, '.restore-%s' % self.service)

		# Cleanup
		shutil.rmtree(temp_store)

	def wipe(self):
		"""
		Wipe player data and reset the game back to default state
		:return:
		"""
		base = self.get_save_directory()
		for file in self.get_save_files():
			file_path = os.path.join(base, file)
			if os.path.isdir(file_path):
				logging.info('Removing directory: %s' % file_path)
				shutil.rmtree(file_path)
			elif os.path.isfile(file_path):
				logging.info('Removing file: %s' % file_path)
				os.remove(file_path)
			else:
				logging.info('Skipping non-present file: %s' % file_path)

	def get_enabled_mods(self) -> list['BaseMod']:
		"""
		Get all enabled mods that are locally available on this service

		:return:
		"""
		# MUST be extended to use; each game registers their mods differently
		return []

	def add_mod(self, mod: 'BaseMod', force: bool = False) -> bool:
		"""
		Install a mod

		:param mod: Mod to install
		:param force: Force the installation even if the mod is already installed
		:return:
		"""
		# MUST be extended to use; each game registers their mods differently
		return False

	def install_mod_dependencies(self, mod: 'BaseMod'):
		"""
		Install the dependencies for a given mod

		:param mod:
		:return:
		"""
		if mod.dependencies:
			for dep in mod.dependencies:
				logging.info('Ensuring dependency %s is installed' % dep)
				dep_mod = self.game.mod_handler.get_mod(self, mod.provider, dep)
				if not dep_mod:
					logging.error('Failed to find dependency %s for mod %s' % (dep, mod.name))
				else:
					self.add_mod(dep_mod)

	def remove_mod(self, mod: 'BaseMod') -> bool:
		"""
		Remove a mod

		Will completely uninstall the requested mod

		:param mod:
		:return:
		"""

		# For additional logic, extend this function with your game-specific logic.
		self.remove_mod_files(mod)
		return True

	def remove_mod_files(self, mod: 'BaseMod'):
		"""
		Remove the files for a given mod

		Will NOT completely remove the mod from the game configuration, so safe to call during reinstall/upgrade.

		:param mod:
		:return:
		"""
		# First pass, remove all files from the mod
		for file in mod.files.values():
			target = os.path.join(self.get_app_directory(), file)
			if os.path.exists(target) and os.path.isfile(target):
				logging.info('Removing file %s' % file)
				os.remove(target)

		# Second pass, remove all directories, any non-empty directory probably contains other files
		for file in mod.files.values():
			target = os.path.join(self.get_app_directory(), file)
			if os.path.exists(target) and os.path.isdir(target):
				if os.listdir(target):
					logging.warning('Directory %s is not empty, skipping removal' % target)
				else:
					logging.info('Removing directory %s' % target)
					os.rmdir(target)

	def get_mod(self, provider: str, mod_id: str | int) -> 'BaseMod | None':
		"""
		Get the locally enabled mod that matches the given provider and mod ID

		:param provider:
		:param mod_id:
		:return:
		"""
		enabled_mods = self.get_enabled_mods()
		for check_mod in enabled_mods:
			if check_mod.provider == provider and str(check_mod.id) == str(mod_id):
				return check_mod
		return None

	def check_mod_files_installed(self, mod: 'BaseMod', mode: str = 'any') -> bool:
		"""
		Check if a given mod already has files installed in the game.

		Useful for a pre-check before a mod is installed to know if it will overwrite an existing file.
		If `mode` is set to 'any' (default behaviour), will return True if ANY file is present.
		else if `mode` is set to 'all', will return True only if ALL files are present.

		:param mod:  Mod to check
		:param mode: Set to "any" or "all" (defaults to any)
		:return:
		"""
		for file in mod.files.values():
			target = os.path.join(self.get_app_directory(), file)
			if target.endswith('/'):
				# Skip directories; these can exist across mods
				continue

			if mode == 'all' and not os.path.exists(target):
				logging.warning('File %s is missing from game' % file)
				return False
			elif mode == 'any' and os.path.exists(target):
				logging.warning('File %s present in game' % file)
				return True
		return True if mode == 'all' else False

	def install_mod_files(self, mod: 'BaseMod') -> bool:
		"""
		Install the files into this game

		:param mod:
		:return:
		"""
		for source, target in mod.files.items():
			target_file = os.path.join(self.get_app_directory(), target)

			# Ensure target directory exists
			utils.makedirs(os.path.dirname(target_file))

			if target_file.endswith('/'):
				# Target is just a directory, ensure it exists.
				logging.info('Creating directory: %s' % target_file)
				utils.makedirs(target_file)
			elif source == '@':
				# Source is the package itself; this just copies the entire mod into the destination.
				source_file = os.path.join(utils.get_base_directory(), 'Packages', mod.package)
				logging.info('Copying %s -> %s' % (source_file, target_file))
				shutil.copy(source_file, target_file)
				utils.ensure_file_ownership(target_file)
			elif source.startswith('@:'):
				# Source is a file within the package, (usually a ZIP archive)
				source_file = source[2:]
				source_archive = os.path.join(utils.get_base_directory(), 'Packages', mod.package)
				if source_archive.endswith('.zip'):
					logging.info('Extracting %s -> %s' % (source_file, target_file))
					with ZipFile(source_archive, 'r') as zip_ref:
						with zip_ref.open(source_file) as f, open(target_file, 'wb') as out_file:
							shutil.copyfileobj(f, out_file)
					utils.ensure_file_ownership(target_file)
				else:
					logging.error('Cannot install mod %s: Package %s is not a ZIP archive' % (mod.name, mod.package))
					return False
			else:
				logging.error('Cannot install mod %s: Invalid source path %s' % (mod.name, source))
				return False
		return True

	def get_version(self) -> str | None:
		"""
		Get the version of the game binary

		:return:
		"""
		return None

	def get_loader(self) -> str | None:
		"""
		Get the loader used to launch the game

		:return:
		"""
		return None
