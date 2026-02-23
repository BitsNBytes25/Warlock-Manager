import json
import logging
import sys
from pathlib import Path
import typer
from typing import Annotated
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.get_wan_ip import get_wan_ip


def app_runner(game: BaseApp):
	app = typer.Typer()

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

	@app.callback()
	def main(
		debug: Annotated[
			bool,
			typer.Option(help='Enable debug logging output', is_flag=True)
		] = False
	):
		if debug:
			logging.basicConfig(level=logging.DEBUG)

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

	arg_max_backups = Annotated[
		int,
		typer.Option(
			help='Maximum number of backups to keep when creating a new backup, or 0 to keep all backups',
		)
	]

	arg_restore = Annotated[
		Path,
		typer.Argument(
			help='Path to backup to restore from',
			exists = True,
			readable = True
		)
	]

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

	@app.command()
	def backup(max_backups: arg_max_backups = 0):
		"""
		Create a backup of the game, keeping a maximum number of backups if specified

		:param max_backups:
		:return:
		"""
		sys.exit(0 if game.backup(max_backups) else 1)

	@app.command()
	def restore(restore_path: arg_restore):
		"""
		Restore a backup of the game from the specified path

		:param restore_path:
		:return:
		"""
		sys.exit(0 if game.restore(str(restore_path)) else 1)

	@app.command()
	def check_update():
		"""
		Check if an update is available for the game

		:return:
		"""
		sys.exit(0 if game.check_update_available() else 1)

	@app.command()
	def update():
		"""
		Update the game to the latest version if an update is available

		:return:
		"""
		sys.exit(0 if game.update() else 1)

	@app.command()
	def delayed_update():
		"""
		Issue a delayed update, providing 1 hour for players to disconnect before updating

		:return:
		"""
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
			svc_stats = {
				'service': svc.service,
				'name': svc.get_name(),
				'ip': get_wan_ip(),
				'port': svc.get_port(),
				'enabled': svc.is_enabled(),
				'max_players': svc.get_player_max(),
			}
			stats[svc.service] = svc_stats
		print(json.dumps(stats))
		sys.exit(0)

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

			pre_exec = svc.get_exec_start_pre_status()
			start_exec = svc.get_exec_start_status()
			if pre_exec and pre_exec['start_time']:
				pre_exec['start_time'] = int(pre_exec['start_time'].timestamp())
			if pre_exec and pre_exec['stop_time']:
				pre_exec['stop_time'] = int(pre_exec['stop_time'].timestamp())
			if start_exec and start_exec['start_time']:
				start_exec['start_time'] = int(start_exec['start_time'].timestamp())
			if start_exec and start_exec['stop_time']:
				start_exec['stop_time'] = int(start_exec['stop_time'].timestamp())

			players = svc.get_players()
			# Some games may not support getting a full player list
			if players is None:
				players = []
				player_count = svc.get_player_count()
			else:
				player_count = len(players)

			svc_stats = {
				'service': svc.service,
				'name': svc.get_name(),
				'ip': get_wan_ip(),
				'port': svc.get_port(),
				'status': status,
				'enabled': svc.is_enabled(),
				'players': players,
				'player_count': player_count,
				'max_players': svc.get_player_max(),
				'memory_usage': svc.get_memory_usage(),
				'cpu_usage': svc.get_cpu_usage(),
				'game_pid': svc.get_game_pid(),
				'service_pid': svc.get_pid(),
				'pre_exec': pre_exec,
				'start_exec': start_exec,
			}
			stats[svc.service] = svc_stats
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

		:return:
		"""
		sys.exit(0 if game.first_run() else 1)

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
