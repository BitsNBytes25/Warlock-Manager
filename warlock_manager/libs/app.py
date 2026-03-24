import logging
import os
import sys

from warlock_manager.libs.get_wan_ip import get_wan_ip
from warlock_manager.libs.tui import print_header, Table, print_subheader, prompt_yn, prompt_text, prompt_options
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService


ICON_ENABLED = '✅'
ICON_STOPPED = '🛑'
ICON_DISABLED = '❌'
ICON_WARNING = '⛔'
ICON_STARTING = '⌛'
ICON_STOPPING = '⌛'


def stringify_value(key, service: BaseService):
	if key == 'Status':
		if service.is_starting():
			return ICON_STARTING + ' Starting'
		elif service.is_stopped():
			return ICON_STOPPED + ' Stopped'
		elif service.is_stopping():
			return ICON_STOPPING + ' Stopping'
		elif service.is_running():
			return ICON_ENABLED + ' Running'
		else:
			return 'Unknown'
	elif key == 'CPU':
		return service.get_cpu_usage()
	elif key == 'Mem':
		return service.get_memory_usage()
	elif key == 'Players':
		return f'{service.get_player_count() or 0} / {service.get_player_max()}'
	elif key == 'Auto-Start':
		return f'{ICON_ENABLED} Enabled' if service.is_enabled() else f'{ICON_DISABLED} Disabled'
	elif key == 'Port':
		return str(service.get_port())
	elif key == 'Service':
		return service.service
	elif key == 'Name':
		return service.get_name()
	elif key == 'Connect':
		ip = get_wan_ip()
		port = service.get_port()
		if ip and port:
			return f'{ip}:{port}'
		elif ip:
			return ip
		elif port:
			return port
		else:
			return 'N/A'
	else:
		return key


def menu_config_option(source: BaseApp | BaseService, option: str):
	val_type = source.get_option_type(option)
	val_opts = source.get_option_options(option)
	val_default = source.get_option_value(option)

	print_subheader(f'Configure {option}')
	print(source.get_option_help(option))
	print('')
	if val_type == 'bool':
		new_val = prompt_yn(prompt=option, default='y' if val_default else 'n')
	elif val_opts:
		new_val = prompt_options(options=val_opts, default=val_default)
	else:
		new_val = prompt_text(prefill=True, default=str(val_default))

	source.set_option(option, new_val)


def menu_config(source: BaseApp | BaseService, configs: list):
	search = ''
	while True:
		groups = {}
		advanced = []
		options_ordered = []

		# Sort the configs alphabetically
		configs.sort()

		# Build the list of grouped configuration options.
		# This is a user assistance feature to keep like-options together
		for opt in configs:
			group = source.get_option_group(opt)
			if group == 'Basic' and isinstance(source, BaseService):
				# Hide Basic options under services as they are already rendered in the service menu.
				continue
			if group not in groups:
				groups[group] = []

			if group == 'Advanced':
				advanced.append(opt)
			else:
				groups[group].append(opt)

		if len(advanced) > 0:
			groups['Advanced'] = advanced

		# Print each config, grouped with their group
		counter = 0
		for group in groups:
			print_subheader(group)
			table = Table(['#', 'Option', 'Value'])

			for opt in groups[group]:
				counter += 1
				options_ordered.append(opt)
				if search and search.lower() not in opt.lower():
					continue
				table.add([str(counter), opt, source.get_option_value(opt)])

			table.render()

		print('')
		if isinstance(source, BaseApp) and source.is_active():
			configurable = False
			logging.warning('Cannot configure options while a service in this game is running.')
		elif isinstance(source, BaseService) and source.is_running():
			configurable = False
			logging.warning('Cannot configure options while this service is running.')
		else:
			configurable = True

		if configurable:
			print(f'Enter 1-{counter}, [B]ack to previous menu, [Q]uit to exit, or enter text to search for an option')
		else:
			print('[B]ack to previous menu, [Q]uit to exit, or enter text to search for an option')
		opt = input(': ').lower()

		if opt.isdigit() and 1 <= int(opt) <= counter:
			if configurable:
				menu_config_option(source, options_ordered[int(opt) - 1])
		elif opt == 'b':
			return
		elif opt == 'q':
			sys.exit(0)
		elif opt == '':
			search = ''
		else:
			search = opt


def menu_service(service: BaseService):
	while True:
		print_header(f'Manage {service.get_name()}')
		table = Table()
		table.align = ['l', 'r', 'l']
		table.borders = False
		input_keys = []

		# Provide the basic controls for this service, start/stop, enable/disable, etc
		if service.is_stopped():
			input_keys.append('S')
			table.add(['[S]tart', 'Status:', stringify_value('Status', service)])
		else:
			input_keys.append('T')
			table.add(['s[T]op', 'Status:', stringify_value('Status', service)])

		if service.is_enabled():
			input_keys.append('D')
			table.add(['[D]isable', 'Auto-Start:', stringify_value('Auto-Start', service)])
		else:
			input_keys.append('E')
			table.add(['[E]nable', 'Auto-Start:', stringify_value('Auto-Start', service)])

		# Provide basic stats; these are not configurable, but are still useful
		table.add(['', 'CPU Usage:', stringify_value('CPU', service)])
		table.add(['', 'Memory Usage:', stringify_value('Mem', service)])
		table.add(['', 'Players:', stringify_value('Players', service)])
		table.add(['', 'Direct Connect:', stringify_value('Connect', service)])

		# Pull the Basic options for this service
		configs = service.get_options()
		options_ordered = []

		# Sort the configs alphabetically
		configs.sort()
		counter = 0
		other_options = []

		for opt in configs:
			group = service.get_option_group(opt)
			# We're only rendering "Basic" configs here
			if group == 'Basic':
				counter += 1
				options_ordered.append(opt)
				table.add([str(counter), opt, service.get_option_value(opt)])
			else:
				other_options.append(opt)

		if len(other_options) > 0:
			input_keys.append('O')
			table.add(['[O]ptions', '', f'View/manage {len(other_options)} other options'])

		table.render()

		print('')
		if counter > 0:
			input_keys = ['1-' + str(counter)] + input_keys

		print('Enter [' + '], ['.join(input_keys) + ']: ')
		# print('Control: [S]tart all | s[T]op all | [R]estart all | [U]pdate')
		# print('Manage Data: [B]ackup all | [W]ipe all')
		print('or [B]ack to menu / [Q]uit to exit')
		opt = input(': ').lower()

		if opt == 'b':
			return
		elif opt == 'q':
			sys.exit(0)
		elif opt.isdigit() and 1 <= int(opt) <= counter:
			if service.is_running():
				logging.warning('Cannot configure options for a service while it is running.')
			else:
				menu_config_option(service, options_ordered[int(opt) - 1])
		elif opt == 'o':
			menu_config(service, other_options)
		elif opt == 's':
			service.start()
		elif opt == 't':
			service.stop()


def default_menu_main(game: BaseApp):
	while True:
		running = game.is_active()
		services = game.get_services()
		print_header('Welcome to the %s Server Manager' % game.desc)
		table = Table(['#', 'Service', 'Name', 'Port', 'Auto-Start', 'Status', 'CPU', 'Mem', 'Players'])
		table.align = ['r', 'l', 'l', 'r', 'l', 'l', 'r', 'r', 'l']
		counter = 0
		for svc in services:
			counter += 1
			row = []
			for col in table.header:
				if col == '#':
					row.append(str(counter))
				else:
					row.append(stringify_value(col, svc))
			table.add(row)
		table.render()

		print('')
		print('1-%s to manage individual map settings' % len(services))
		print('Configure: global [O]ptions')
		print('Control: [S]tart all | s[T]op all | [R]estart all | [U]pdate')
		print('Manage Data: [B]ackup all | [W]ipe all')
		print('or [Q]uit to exit')
		opt = input(': ').lower()

		if opt != 'q':
			os.system('clear')

		if opt.isdigit() and 1 <= int(opt) <= len(services):
			# Menu control / details
			menu_service(services[int(opt) - 1])
		elif opt == 'b':
			# Manage Data: Backup All
			if running:
				print('⚠️  Please stop all maps before managing backups.')
			else:
				for svc in game.get_services():
					svc.backup()
		# @todo mods
		elif opt == 'o':
			menu_config(game, game.get_options())
		elif opt == 'q':
			sys.exit(0)
		elif opt == 's':
			game.start_all()
		elif opt == 't':
			game.stop_all()
		elif opt == 'r':
			game.restart_all()
		elif opt == 'u':
			if running:
				print('⚠️  Please stop all maps before updating.')
			else:
				game.update()
		elif opt == 'w':
			if running:
				print('⚠️  Please stop all maps before wiping data.')
			else:
				# @todo
				pass
