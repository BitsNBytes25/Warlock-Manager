import json
import logging
import inspect
import sys
import typer
from typing import Annotated
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.sensitive_data_filter import sensitive_data_filter


class ClassNameFilter(logging.Filter):
	def filter(self, record):
		# Try to get the class name from the call stack
		frame = inspect.currentframe()
		while frame:
			if 'self' in frame.f_locals:
				class_name = frame.f_locals['self'].__class__.__name__
				if class_name not in ['ClassNameFilter', 'RootLogger']:
					record.classname = frame.f_locals['self'].__class__.__name__
					break
			frame = frame.f_back
		else:
			record.classname = ''
		return True


def app_runner(game: BaseApp):
	app = typer.Typer()

	features = game.features - game.disabled_features

	def resolve_service(ctx: typer.Context, value: str | None) -> None | BaseService:
		"""
		Resolve the service directive to an actual service instance, or return None if no service was specified

		:param ctx:
		:param value:
		:return: BaseService | None
		"""
		if value is None:
			return None
		services = game.get_services()
		for svc in services:
			if svc.service == value:
				return svc
		raise typer.BadParameter('Service instance %s not found!' % value)

	arg_debug = Annotated[
		bool,
		typer.Option(
			help='Enable debug logging output',
			is_flag=True
		)
	]

	arg_service_optional = Annotated[
		str | None,
		typer.Option(
			help='Name of service instance, or omit for all instances',
			callback=resolve_service
		)
	]

	arg_service_required = Annotated[
		str,
		typer.Option(
			help='Name of service instance',
			callback=resolve_service
		)
	]

	arg_service_name_required = Annotated[
		str,
		typer.Option(
			help='Name of service instance'
		)
	]

	arg_max_backups = Annotated[
		int,
		typer.Option(
			help='Maximum number of backups to keep when creating a new backup, or 0 to keep all backups',
		)
	]

	arg_restore = Annotated[
		str,
		typer.Argument(
			help='Path to backup to restore from'
		)
	]

	@app.callback()
	def main(
		debug: arg_debug = False
	):
		log_level = logging.DEBUG if debug else logging.INFO
		logging.basicConfig(
			level=log_level,
			format='%(asctime)s [%(levelname)s] %(classname)s.%(funcName)s: %(message)s',
			force=True
		)
		logging.getLogger().addFilter(ClassNameFilter())
		logging.getLogger().addFilter(sensitive_data_filter)

		if debug:
			logging.debug('Debug logging enabled')

	@app.command()
	def start(service: arg_service_optional = None):
		"""
		Start a service instance, or all instances if no service is specified

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			service.start()
		else:
			game.start_all()

	@app.command()
	def restart(service: arg_service_optional = None):
		"""
		Restart a service instance, or all instances if no service is specified

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			service.restart()
		else:
			game.restart_all()
		sys.exit(0)

	if 'api' in features:
		@app.command()
		def delayed_restart(service: arg_service_optional = None):
			"""
			Issue a delayed restart, providing 1 hour for players to disconnect before restarting

			:param service:
			:return:
			"""
			if service and isinstance(service, BaseService):
				service.delayed_restart()
			else:
				game.delayed_restart_all()
			sys.exit(0)

	@app.command()
	def stop(service: arg_service_optional = None):
		"""
		Stop a service instance, or all instances if no service is specified

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			service.stop()
		else:
			game.stop_all()
		sys.exit(0)

	if 'api' in features:
		@app.command()
		def delayed_stop(service: arg_service_optional = None):
			"""
			Issue a delayed stop, providing 1 hour for players to disconnect

			:param service:
			:return:
			"""
			if service and isinstance(service, BaseService):
				service.delayed_stop()
			else:
				game.delayed_stop_all()
			sys.exit(0)

	if 'api' in features and 'cmd' in features:
		@app.command()
		def cmd(service: arg_service_required, command: str):
			"""
			Send a command to the game server via the service API

			:param service:
			:param command:
			:return:
			"""
			result = service.cmd(command)
			if result is not None:
				print(result)
				sys.exit(0)
			else:
				sys.exit(1)

	if 'api' in features and 'cmd' in features:
		@app.command()
		def get_commands(service: arg_service_required):
			"""
			Get a list of available commands for the service API in JSON format
			"""
			cmds = service.get_commands()
			if cmds is None:
				sys.exit(1)
			else:
				print(json.dumps(cmds))
				sys.exit(0)

	@app.command()
	def backup(service: arg_service_optional = None, max_backups: arg_max_backups = 0):
		"""
		Create a backup of the game, keeping a maximum number of backups if specified
		"""
		if service and isinstance(service, BaseService):
			sys.exit(0 if service.backup(max_backups) else 1)
		else:
			if len(game.get_services()) == 0:
				logging.warning('No services are available for backup, nothing to do.')
				sys.exit(1)
			success = True
			for svc in game.get_services():
				if not svc.backup(max_backups):
					success = False
			sys.exit(0 if success else 1)

	@app.command()
	def restore(service: arg_service_required, restore_path: arg_restore):
		"""
		Restore a backup of the game from the specified path

		:param restore_path:
		:return:
		"""
		sys.exit(0 if service.restore(str(restore_path)) else 1)

	@app.command()
	def check_update(service: arg_service_optional = None):
		"""
		Check if an update is available for the game

		:return:
		"""
		if service:
			sys.exit(0 if service.check_update_available() else 1)
		else:
			sys.exit(0 if game.check_update_available() else 1)

	@app.command()
	def update(service: arg_service_optional = None):
		"""
		Update the game to the latest version if an update is available

		:return:
		"""
		if service:
			sys.exit(0 if service.update() else 1)
		else:
			sys.exit(0 if game.update() else 1)

	if 'api' in features:
		@app.command()
		def delayed_update(service: arg_service_optional = None):
			"""
			Issue a delayed update, providing 1 hour for players to disconnect before updating

			:return:
			"""
			if service:
				service.delayed_update()
			else:
				game.delayed_update()
			sys.exit(0)

	@app.command()
	def pre_stop(service: arg_service_required):
		"""
		Send notifications and perform any necessary pre-stop tasks for a service instance

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			sys.exit(0 if service.pre_stop() else 1)
		else:
			sys.exit(1)

	@app.command()
	def post_start(service: arg_service_required):
		"""
		Send notifications and perform any necessary post-start tasks for a service instance

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			sys.exit(0 if service.post_start() else 1)
		else:
			sys.exit(1)

	@app.command()
	def get_services():
		"""
		Get the list of all services for this game in JSON format

		:return:
		"""
		services = game.get_services()
		stats = {}
		for svc in services:
			stats[svc.service] = svc.get_info()
		print(json.dumps(stats))
		sys.exit(0)

	if 'create_service' in features:
		@app.command()
		def create_service(service: arg_service_name_required):
			"""
			Create a new service instance for the game with the specified name

			:param service:
			:return:
			"""
			try:
				new_service = game.create_service(service)
				print('CreatedService:' + new_service.service)
				sys.exit(0)
			except Exception as e:
				print('Error creating service instance: %s' % str(e), file=sys.stderr)
				sys.exit(1)

	if 'create_service' in features:
		@app.command()
		def remove_service(service: arg_service_name_required):
			"""
			Remove a service instance for the game with the specified name

			:param service:
			:return:
			"""
			try:
				game.remove_service(service)
				sys.exit(0)
			except Exception as e:
				print('Error removing service instance: %s' % str(e), file=sys.stderr)
				sys.exit(1)

	@app.command()
	def get_metrics(service: arg_service_optional = None):
		"""
		Get performance metrics in JSON format

		:param service: BaseService | None
		:return:
		"""
		if service and isinstance(service, BaseService):
			services: list[BaseService] = [service]
		else:
			services: list[BaseService] = game.get_services()

		stats = {}
		for svc in services:
			if svc.is_starting():
				status = 'starting'
			elif svc.is_stopping():
				status = 'stopping'
			elif svc.is_running():
				status = 'running'
			else:
				status = 'stopped'

			players = svc.get_players()
			# Some games may not support getting a full player list
			if players is None:
				players = []
				player_count = svc.get_player_count()
			else:
				player_count = len(players)

			svc_stats = {
				'status': status,
				'players': players,
				'player_count': player_count,
				'memory_usage': svc.get_memory_usage(),
				'cpu_usage': svc.get_cpu_usage(),
				'game_pid': svc.get_game_pid(),
				'service_pid': svc.get_pid(),
				'ports': svc.get_ports(),
			}
			stats[svc.service] = svc.get_info() | svc_stats
		print(json.dumps(stats))
		sys.exit(0)

	@app.command()
	def get_configs(service: arg_service_optional = None):
		"""
		Get the list of configuration options for the game or a specific service instance in JSON format

		:param service:
		:return:
		"""
		opts = []
		if service:
			source = service
		else:
			source = game

		for opt in source.get_options():
			opts.append({
				'option': opt,
				'default': source.get_option_default(opt),
				'value': source.get_option_value(opt),
				'type': source.get_option_type(opt),
				'help': source.get_option_help(opt),
				'options': source.get_option_options(opt),
				'group': source.get_option_group(opt)
			})
		print(json.dumps(opts))
		sys.exit(0)

	@app.command()
	def get_ports(service: arg_service_optional = None):
		"""
		Get the list of port definitions for the game or a specific service instance in JSON format

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			services: list[BaseService] = [service]
		else:
			services: list[BaseService] = game.get_services()

		ports = []
		for svc in services:
			for port_dat in svc.get_port_definitions():
				port_def = {}
				if isinstance(port_dat[0], int):
					# Port statically assigned and cannot be changed
					port_def['value'] = port_dat[0]
					port_def['config'] = None
				else:
					port_def['value'] = svc.get_option_value(port_dat[0])
					port_def['config'] = port_dat[0]

				port_def['service'] = svc.service
				port_def['protocol'] = port_dat[1]
				port_def['description'] = port_dat[2]
				ports.append(port_def)
		print(json.dumps(ports))
		sys.exit(0)

	@app.command()
	def set_config(option: str, value: str, service: arg_service_optional = None):
		"""
		 Set a configuration option for the game or a specific service instance

		:param option:
		:param value:
		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			service.set_option(option, value)
		else:
			game.set_option(option, value)
		sys.exit(0)

	@app.command()
	def first_run():
		"""
		Perform first-run configuration for the game
		"""
		sys.exit(0 if game.first_run() else 1)

	@app.command()
	def remove(confirm: bool = False):
		"""
		Remove all game data, including configuration and services. Use with extreme caution!
		"""
		if not confirm:
			print(
				'To remove all game data, run this command with the --confirm flag. '
				'This will delete all configuration and service data for the game.'
			)
			sys.exit(1)

		game.remove()
		sys.exit(0)

	if 'api' in features:
		@app.command()
		def has_players(service: arg_service_optional = None):
			"""
			Check if there are players currently connected, exits 0 if there are players, 1 if there are not.

			:param service:
			:return:
			"""
			if service and isinstance(service, BaseService):
				services: list[BaseService] = [service]
			else:
				services: list[BaseService] = game.get_services()

			players = False
			for svc in services:
				c = svc.get_player_count()
				if c is None:
					print('%s cannot determine player count' % svc.get_name())
				elif c == 0:
					print('%s has no players connected' % svc.get_name())
				else:
					print('%s has %d player(s) connected' % (svc.get_name(), c))
					players = True

			sys.exit(0 if players else 1)

	@app.command()
	def is_running(service: arg_service_optional = None):
		"""
		Check if a service instance is currently running, exits 0 if at least one instance is running, else 1.

		:param service:
		:return:
		"""
		if service and isinstance(service, BaseService):
			services: list[BaseService] = [service]
		else:
			services: list[BaseService] = game.get_services()

		running = False
		for svc in services:
			if svc.is_running():
				print('%s is running' % svc.get_name())
				running = True
			else:
				print('%s is not running' % svc.get_name())

		sys.exit(0 if running else 1)

	return app
