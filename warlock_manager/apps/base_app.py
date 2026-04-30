import json
import os
import shutil
import time
from abc import ABC
from urllib import request
from urllib import error as urllib_error
from typing import TYPE_CHECKING, Optional

from typing_extensions import deprecated

if TYPE_CHECKING:
	from warlock_manager.services.base_service import BaseService
	from warlock_manager.mods.base_mod import BaseMod

from warlock_manager.libs.tui import prompt_yn, prompt_text
from warlock_manager.libs import utils
from warlock_manager.libs.ports import get_ports
from warlock_manager.libs.logger import logger


class BaseApp(ABC):
	"""
	Game application manager
	"""

	def __init__(self):
		self.name = ''
		"""
		:type str:
		Short name for this game
		"""

		self.desc = ''
		"""
		:type str:
		Description / full name of this game
		"""

		self.services = self.detect_services()
		"""
		:type list<str>:
		List of available services (instances) for this game
		"""

		self._svcs = None
		"""
		:type list<BaseService>:
		Cached list of service instances for this game
		"""

		self.service_handler: 'BaseService' = None
		"""
		Specific service to handle for this specific game
		"""

		self.mod_handler: 'BaseMod' = None
		"""
		Specific mod handler to use for this specific game
		"""

		self.service_prefix = ''
		"""
		:type str:
		Prefix to use when creating new services.
		Useful to keep them grouped together in systemd.
		"""

		self.configs = {}
		"""
		:type dict<str, BaseConfig>:
		Dictionary of configuration files for this game
		"""

		self.configured = False
		"""
		:type bool:
		Set to True once configuration files are loaded
		"""

		self.multi_binary = False
		"""
		:type bool:
		Set to True if this game has separate binaries for each service
		"""

		self.features = {
			'api',  # Game supports baseline API features
			'cmd',  # Game supports commands sent via the API
			'create_service',  # Game supports creating new services
		}
		"""
		List of features available in this game
		"""

		self.disabled_features = {''}
		"""
		List of disabled features for this game

		Available features that can be disabled:

		* api
		* cmd
		* create_service
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
				utils.ensure_file_parent_exists(config.path)

	def save(self):
		"""
		Save the configuration files back to disk
		:return:
		"""
		for config in self.configs.values():
			config.save()

	def get_options(self) -> list:
		"""
		Get a list of available configuration options for this game
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
		Get a configuration option from the game config
		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_value(option)

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
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

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
		return ''

	def get_option_type(self, option: str) -> str:
		"""
		Get the type of configuration option from the game config
		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.get_type(option)

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
		return ''

	def get_option_help(self, option: str) -> str:
		"""
		Get the help text of a configuration option from the game config
		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.options[option].help

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
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

	def set_option(self, option: str, value: str | int | bool) -> bool:
		"""
		Set a configuration option in the game config
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
				if previous_value == new_value:
					# No change
					return True

				config.set_value(option, value)
				config.save()

				# Allow the extending service to handle any special actions needed for this option update
				post_result = self.option_value_updated(option, previous_value, new_value)
				if post_result is True:
					# Post-update either returned a successful operation or nothing at all, either is fine.
					logger.info('Updated option %s to %s and ran post-update actions successfully' % (option, value))
					return True
				elif post_result is None:
					logger.debug('Post-update returned None, this is fine as it indicates no post-actions taken')
					logger.info('Updated option %s to %s' % (option, value))
					return True
				else:
					# Post-update explictly returned False, this indicates a problem occurred.
					logger.warning('Configuration saved, but unable to complete post-update actions!')
					return False

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
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

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
		return []

	def get_option_group(self, option: str):
		"""
		Get the display group for a configuration option
		:param option:
		:return:
		"""
		for config in self.configs.values():
			if option in config.options:
				return config.options[option].group

		logger.warning('Invalid option: %s, not present in game configuration!' % option)
		return 'Options'

	def prompt_option(self, option: str):
		"""
		Prompt the user to set a configuration option for the game
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

	def is_active(self) -> bool:
		"""
		Check if any service instance is currently running or starting
		:return:
		"""
		for svc in self.get_services():
			if svc.is_running() or svc.is_starting() or svc.is_stopping():
				return True
		return False

	def stop_all(self):
		"""
		Stop all services with a 5-minute warning to players.

		:return:
		"""
		for service in self.get_services():
			if service.is_running():
				service.stop()

	def delayed_stop_all(self):
		"""
		Perform a delayed stop of all services, giving players time to log off safely before stopping the server.

		Provides a 1-hour warning with 5-minute notifications, then stops all services.
		This is intended to be used when performing maintenance or updates that require downtime,
		but you want to give players a chance to log off safely before the server goes down.

		:return:
		"""
		self._delayed_action('stop')

	def restart_all(self):
		"""
		Restart all services with a 5-minute warning to players.

		:return:
		"""
		for service in self.get_services():
			if service.is_running():
				service.restart()

	def delayed_restart_all(self):
		"""
		Perform a delayed restart of all services, giving players time to log off safely before restarting the server.

		Provides a 1-hour warning with 5-minute notifications, then restarts all services.
		This is intended to be used when performing maintenance or updates that require downtime,
		but you want to give players a chance to log off safely before the server goes down.

		:return:
		"""
		self._delayed_action('restart')

	def start_all(self):
		"""
		Start all services that are enabled for auto-start.

		:return:
		"""
		for svc in self.get_services():
			if svc.is_enabled():
				svc.start()
			else:
				print('Skipping %s as it is not enabled for auto-start.' % svc.service)

	def delayed_update(self):
		"""
		Perform a delayed update of the game, giving players time to log off safely before restarting the server.

		Provides a 1-hour warning with 5-minute notifications, then updates the game and restarts all services.
		This is intended to be used when performing maintenance or updates that require downtime,
		but you want to give players a chance to log off safely before the server goes down.

		:return:
		"""
		self._delayed_action('update')

	def _delayed_action(self, action):
		"""
		If players are logged in, send 5-minute notifications for an hour before stopping the server

		This action applies to ALL game instances under this application.

		:param action:
		:return:
		"""

		if action not in ['stop', 'restart', 'update']:
			logger.error('Invalid action for delayed action: %s' % action)
			return

		if os.geteuid() != 0:
			logger.error('Unable to %s game service unless run with sudo' % action)
			return

		msg = self.get_option_value('%s_delayed' % action)
		if msg == '':
			msg = 'Server will %s in {time} minutes. Please prepare to log off safely.' % action

		start = round(time.time())
		services_running = []
		services = self.get_services()

		logger.info(
			'Starting delayed %s action for all services, this gives current players up to an hour to log off safely' %
			action
		)

		while True:
			still_running = False
			minutes_left = 55 - ((round(time.time()) - start) // 60)
			player_msg = msg
			if '{time}' in player_msg:
				player_msg = player_msg.replace('{time}', str(minutes_left))

			for service in services:
				if service.is_running():
					still_running = True
					if service.service not in services_running:
						services_running.append(service.service)

					player_count = service.get_player_count()

					if player_count == 0 or player_count is None:
						# No players online, stop the service
						logger.info('Stopping %s as no players are online.' % service.service)
						service.stop()
					else:
						# Still online, check to see if we should send a message

						if minutes_left <= 5:
							# Once the timer hits 5 minutes left, drop to the standard stop procedure.
							service.stop()

						if minutes_left % 5 == 0 and minutes_left > 5:
							# Send the warning every 5 minutes
							service.send_message(player_msg)

			if minutes_left % 5 == 0 and minutes_left > 5:
				logger.info('%s minutes remaining before %s.' % (str(minutes_left), action))

			if not still_running or minutes_left <= 0:
				# No services are running, stop the timer
				break

			time.sleep(60)

		if action == 'update':
			# Now that all services have been stopped, perform the update
			self.update()

		if action == 'restart' or action == 'update':
			# Now that all services have been stopped, restart any that were running before
			for service in services:
				if service.service in services_running:
					logger.info('Starting %s' % service.service)
					service.start()

	def get_services(self) -> list['BaseService']:
		"""
		Get a dictionary of available services (instances) for this game

		:return:
		"""
		if self._svcs is None:
			if not self.service_handler:
				raise Exception('No service defined for this game - please ensure to set `self.service_handler`')
			self._svcs = []
			for svc in self.services:
				self._svcs.append(self.service_handler(svc, self))
		return self._svcs

	def get_service(self, service_name: str) -> Optional['BaseService']:
		"""
		Get a specific service instance by name

		:param service_name:
		:return: BaseService instance or None if not found
		"""
		for svc in self.get_services():
			if svc.service == service_name:
				return svc
		return None

	def check_update_available(self) -> bool:
		"""
		Check if there's an update available for this game

		:return:
		"""
		if self.multi_binary:
			for svc in self.get_services():
				if svc.check_update_available():
					return True
		return False

	def update(self) -> bool:
		"""
		Update the game server

		:return:
		"""
		if self.multi_binary:
			ret = True
			for svc in self.get_services():
				if not svc.update():
					ret = False
			if not ret:
				logger.warning('One or more services failed to update, please check the logs for more information.')
			return ret
		return False

	def post_update(self):
		"""
		Perform any post-update actions needed for this game

		Called immediately after an update is performed but before services are restarted.

		:return:
		"""
		pass

	def get_next_available_port(self, service, port: int, protocol: str) -> int:
		"""
		Search through all ports used by all services under this game and find the next available one.

		:param service: The service instance that started the lookup, (its ports will be checked too)
		:param port:
		:param protocol:
		:return:
		"""
		if len(self.get_services()) == 0:
			# If there are no services here, just return the original port.
			return port

		protocol = protocol.lower()

		# Preseed the list of used ports with the ports currently in use by the system
		used_ports = get_ports(protocol)
		candidate_services = [service] + self.get_services()
		for svc in candidate_services:
			port_defs = svc.get_port_definitions()
			for port_def in port_defs:
				if port_def[1].lower() == protocol:
					if isinstance(port_def[0], int):
						port_val = port_def[0]
					else:
						port_val = svc.get_option_value(port_def[0])

					if svc == service and port_val == port:
						# This is the original port we're trying to find a replacement for, so skip it in the used ports list
						continue

					used_ports.add(port_val)

		# Find the next available port
		candidate = port
		while candidate in used_ports:
			candidate += 1
		return candidate

	def send_discord_message(self, message: str):
		"""
		Send a message to the configured Discord webhook

		:param message:
		:return:
		"""
		if not self.get_option_value('Discord Enabled'):
			print('Discord notifications are disabled.')
			return

		if self.get_option_value('Discord Webhook URL') == '':
			print('Discord webhook URL is not set.')
			return

		print('Sending to discord: ' + message)
		req = request.Request(
			self.get_option_value('Discord Webhook URL'),
			headers={
				'Content-Type': 'application/json',
				'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0'
			},
			method='POST'
		)
		data = json.dumps({'content': message}).encode('utf-8')
		try:
			with request.urlopen(req, data=data):
				pass
		except urllib_error.HTTPError as e:
			print('Could not notify Discord: %s' % e)

	@deprecated("Please use get_base_directory() from utils instead.")
	def get_app_directory(self) -> str:
		"""
		Get the base directory for this game installation.

		This directory usually will contain manage.py, AppFiles, Backups, and other related files.

		:return:
		"""
		return utils.get_base_directory()

	@deprecated("Please use get_home_directory() from utils instead")
	def get_home_directory(self) -> str:
		"""
		Get the home directory of the user running this application

		:return:
		"""
		return utils.get_home_directory()

	def create_service(self, service_name: str) -> 'BaseService':
		"""
		Create a new service instance for this game with the given name

		:param service_name:
		:return:
		"""
		if not self.service_handler:
			raise Exception('No service defined for this game - please ensure to set `self.service_handler`')

		if self.service_prefix == '':
			raise Exception('Service prefix cannot be empty!')

		# Simple validation of service name; should only contain lowercase letters and dashes.
		if not service_name.islower() or not all(c.isalnum() or c == '-' for c in service_name):
			raise Exception(
				'Invalid service name: %s. Service names should only contain lowercase letters, numbers, and dashes.' %
				service_name
			)

		if service_name == '':
			raise Exception('Service name cannot be empty!')

		if self.service_prefix:
			if not service_name.startswith(self.service_prefix):
				service_name = self.service_prefix + service_name

		if service_name.endswith('-'):
			raise Exception('Service name cannot end with a dash!')

		if service_name.startswith('-'):
			raise Exception('Service name cannot start with a dash!')

		if os.path.exists('/etc/systemd/system/%s.service' % service_name):
			raise Exception('Service instance %s already exists!' % service_name)

		svc = self.service_handler(service_name, self)
		svc.create_service()

		# Add the new service to this list so it's immediately available
		if self._svcs is None:
			self._svcs = []
		self._svcs.append(svc)
		self.services.append(service_name)

		return svc

	def remove(self):
		"""
		Remove this game and all instances under it

		:return:
		"""

		for svc in self.get_services():
			svc.remove_service()

		self.services = []
		self._svcs = None

		# Cleanup configurations
		for config in self.configs.values():
			if config.path and os.path.exists(config.path):
				os.remove(config.path)
				logger.info('Removed config file for %s at %s' % (self.name, config.path))

		# Cleanup directory structure
		shutil.rmtree(os.path.join(utils.get_base_directory(), 'AppFiles'))
		shutil.rmtree(os.path.join(utils.get_base_directory(), 'Environments'))

	def remove_service(self, service_name: str):
		"""
		Remove a service instance for this game with the given name

		:param service_name:
		:return:
		"""
		svc = self.get_service(service_name)
		if not svc:
			raise Exception('Service instance %s does not exist!' % service_name)

		svc.remove_service()

		if self._svcs is not None:
			self._svcs = [s for s in self._svcs if s.service != service_name]
		if service_name in self.services:
			self.services.remove(service_name)

	def detect_services(self) -> list:
		"""
		Try to detect available services for this game.
		:return:
		"""
		envs = os.path.join(utils.get_base_directory(), 'Environments')
		if os.path.exists(envs):
			# Each service should have a file here, named as {service}.env
			services = []
			files = os.listdir(envs)
			for f in files:
				if f.endswith('.env') and os.path.isfile(os.path.join(envs, f)):
					services.append(f[:-4])
			return services
		return []

	@deprecated("Please use get_app_uid() from utils instead")
	def get_app_uid(self) -> int:
		"""
		Get the user ID that should own the game files, based on the ownership of the executable directory
		:return:
		"""
		return utils.get_app_uid()

	@deprecated("Please use get_app_gid() from utils instead")
	def get_app_gid(self) -> int:
		"""
		Get the group ID that should own the game files, based on the ownership of the executable directory
		:return:
		"""
		return utils.get_app_gid()

	def first_run(self) -> bool:
		"""
		Perform any first-run configuration needed for this game

		:return:
		"""

		# Ensure some baseline directories exist with the correct ownership and permissions
		utils.makedirs(os.path.join(utils.get_base_directory(), 'Backups'))
		utils.makedirs(os.path.join(utils.get_base_directory(), 'AppFiles'))
		utils.makedirs(os.path.join(utils.get_base_directory(), 'Environments'))

		return True

	@deprecated("Please use ensure_file_ownership() from utils instead")
	def ensure_file_ownership(self, file: str):
		"""
		Try to set the ownership of the given file to match the ownership of the game installation directory.
		:param file:
		:return:
		"""
		return utils.ensure_file_ownership(file)

	@deprecated("Please use ensure_file_parent_exists() from utils instead")
	def ensure_file_parent_exists(self, file: str):
		"""
		A replacement of os.makedirs, but also sets permissions as it creates the directories.

		This variation expects a child file to be requested.
		It will create the parent directory if it does not exist, but will not touch the actual file itself.

		:param file:
		:return:
		"""
		return utils.ensure_file_parent_exists(file)

	@deprecated("Please use makedirs() from utils instead")
	def makedirs(self, target_dir: str):
		"""
		A replacement of os.makedirs, but also sets permissions as it creates the directories.

		:param target_dir:
		:return:
		"""
		return utils.makedirs(target_dir)
