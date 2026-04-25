import os
import sys

from warlock_manager.nexus.nexus import Nexus
from warlock_manager.libs.meta import get_meta
from warlock_manager.libs.get_wan_ip import get_wan_ip
from warlock_manager.libs.tui import print_header, Table, print_subheader, prompt_yn, prompt_text, prompt_options, \
	prompt_long_text
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.logger import logger


ICON_ENABLED = '✅'
ICON_STOPPED = '🛑'
ICON_DISABLED = '❌'
ICON_WARNING = '⛔'
ICON_STARTING = '⌛'
ICON_STOPPING = '⌛'
ICON_GLOBE = '🌐'
ICON_LOCKED = '🔒'
ESCAPE_STRIKE = '\u001b[9m'
ESCAPE_RESET = '\u001b[0m'

AUTH_TOKEN = None


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
			table = Table(['#', 'Option', 'Value'])

			for opt in groups[group]:
				counter += 1
				options_ordered.append(opt)
				if search and search.lower() not in opt.lower() and search.lower() not in group.lower():
					continue
				table.add([str(counter), opt, source.get_option_value(opt)])

			if len(table.data) > 0:
				print_subheader(group)
				table.render()

		print('')
		if isinstance(source, BaseApp) and source.is_active():
			configurable = False
			print('Cannot configure options while a service in this game is running.')
		elif isinstance(source, BaseService) and not source.is_stopped():
			configurable = False
			print('Cannot configure options while this service is running.')
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


def menu_mods_search(source: BaseService, query: str):
	while True:
		print_header('Mods Search')

		locked = not source.is_stopped()
		table = Table(['#', 'Author', 'Mod', 'Installed', 'Version', 'Provider'])

		results = source.game.mod_handler.find_mods(source, query)
		current_mods = source.get_enabled_mods()

		counter = 0
		for mod in results:
			counter += 1

			# Check to see if this mod is already installed, just to show reference to the user.
			current = 'N/A'
			for current_mod in current_mods:
				if mod.id == current_mod.id and mod.author == current_mod.author:
					current = current_mod.version
					break

			table.add(
				[f'[{str(counter)}]' if not locked else ICON_LOCKED,
				 mod.author,
				 mod.name,
				 current,
				 mod.version,
				 mod.get_provider_title()
				 ])

		table.render()
		print('')
		if locked:
			print('Installing is disabled while game is running')
			print('[B]ack, [Q]uit, or search again')
		else:
			print(f'[1-{counter}] to install mod, [B]ack, [Q]uit, or search again')
		opt = input(': ').lower()
		if not locked and opt.isdigit() and 1 <= int(opt) <= counter:
			source.add_mod(results[int(opt) - 1])
			return
		elif opt == '' or opt == 'b':
			return
		elif opt == 'q':
			sys.exit(0)
		else:
			query = opt


def menu_mods(source: BaseService):
	while True:
		add_help = None
		handler = None
		print_header('Mods Management')

		table = Table(['#', 'Author', 'Mod', 'Version', 'Provider'])

		configurable = source.is_stopped()
		handler = source.game.mod_handler

		if handler is not None:
			if hasattr(handler, 'find_mods'):
				add_help = handler.find_mods.__doc__
				if add_help is not None:
					add_help = add_help.strip().split('\n')[0].strip()
				else:
					logger.debug('Mod handler does not provide help for mods search.')
			else:
				logger.debug('Mod handler does not support mods search.')
		else:
			logger.error('Mod handler is not available for this application.')
			return

		counter = 0
		mods = source.get_enabled_mods()
		for mod in mods:
			counter += 1
			if configurable:
				table.add([f'[{str(counter)}]', mod.author, mod.name, mod.version, mod.get_provider_title()])
			else:
				table.add([ICON_LOCKED, mod.author, mod.name, mod.version, mod.get_provider_title()])

		print('')
		if len(table.data) > 0:
			table.render()
			print('')
			if configurable:
				print(f'[1-{counter} to remove mod')
			else:
				print('Managing of mods is disabled while service is active')
		else:
			print('No mods installed.')
			print('')

		if configurable and add_help:
			print('Enter text to search for a mod')
			print(add_help)
		print('or [B]ack to previous menu, [Q]uit to exit')
		opt = input(': ').lower()
		if opt.isdigit() and 1 <= int(opt) <= counter:
			if configurable and prompt_yn('Are you sure you want to remove this mod?', default='n'):
				source.remove_mod(mods[int(opt) - 1])
		elif opt == 'b':
			return
		elif opt == 'q':
			sys.exit(0)
		elif opt != '' and add_help:
			menu_mods_search(source, opt)


def menu_backup(service: BaseService):
	while True:
		print_header(f'Backup {service.get_name()}')

		table = Table()
		table.borders = False

		table.add(['[1]', 'Create New Backup'])
		counter = 1
		for file in os.listdir(service.get_backup_directory()):
			if file.endswith('.tar.gz'):
				counter += 1
				table.add([f'[{str(counter)}]', f'Restore {file}'])

		print('')
		table.render()

		print('')
		print(f'[1-{counter}, [B]ack to previous menu, [Q]uit to exit')
		opt = input(': ').lower()

		if opt.isdigit() and 1 <= int(opt) <= counter:
			if opt == '1':
				service.backup()
			else:
				file = os.listdir(service.get_backup_directory())[int(opt) - 2]
				print(f'Are you sure you want to restore from {file}?')
				print('This will overwrite all current data for this service.')
				print('')
				if prompt_yn('Continue with Restore?', default='n'):
					service.restore(file)
				else:
					print('Restore cancelled.')
		elif opt == 'b':
			return
		elif opt == 'q':
			sys.exit(0)


def menu_service(service: BaseService):
	features = service.game.features - service.game.disabled_features
	nexus = Nexus()

	while True:
		print_header(f'Manage {service.get_name()}')
		table = Table()
		table.align = ['r', 'l', 'l']
		table.borders = False
		port_configs = []
		counter = 0
		options_ordered = []

		# Push some metrics to Nexus if enabled.
		nexus.service_details(service)

		# Provide basic stats; these are not configurable, but are still useful
		table.add(['Status:', '', stringify_value('Status', service)])
		table.add(['Auto-Start:', '', stringify_value('Auto-Start', service)])
		table.add(['CPU Usage:', '', stringify_value('CPU', service)])
		table.add(['Memory Usage:', '', stringify_value('Mem', service)])
		table.add(['Players:', '', stringify_value('Players', service)])
		table.add(['Direct Connect:', '', stringify_value('Connect', service)])
		for port in service.get_ports():
			if port['option'] is not None:
				# Configurable port parameter
				counter += 1
				port_configs.append(port['option'])
				options_ordered.append(port['option'])
				configurable = service.is_stopped()
			else:
				configurable = False

			port_data = []
			port_data.append(str(port['port']))
			port_data.append('(' + port['protocol'].upper() + ')')
			if port['listening']:
				if port['global']:
					port_data.append(f'{ICON_GLOBE} Globally Listening')
				else:
					port_data.append(f'{ICON_DISABLED} Limited Access')

				if port['open']:
					port_data.append(f'{ICON_ENABLED} Open')
				else:
					port_data.append(f'{ICON_LOCKED} Restricted')
			else:
				port_data.append(f'{ICON_DISABLED} Not Listening')

			table.add([port['description'] + ':', f'[{counter}]' if configurable else '', ' '.join(port_data)])

		# Pull the Basic options for this service
		configs = service.get_options()

		# Sort the configs alphabetically
		configs.sort()
		other_options = []

		for opt in configs:
			group = service.get_option_group(opt)
			# We're only rendering "Basic" configs here
			if group == 'Basic':
				if opt not in port_configs:
					counter += 1
					options_ordered.append(opt)
					if service.is_running():
						table.add([opt + ':', '', service.get_option_value(opt)])
					else:
						table.add([opt + ':', f'[{str(counter)}]', service.get_option_value(opt)])
			else:
				other_options.append(opt)

		print('')
		table.render()
		print('')

		controls_configure = []
		controls_control = []
		controls_data = []

		if counter > 0 and not service.is_running():
			controls_configure.append(f'[1-{str(counter)}]')
		controls_configure.append('other [O]ptions')

		if 'mods' in features and service.game.mod_handler is not None:
			controls_configure.append('[M]ods')

		if service.is_stopped():
			controls_control.append('[S]tart')
		else:
			controls_control.append('s[T]op')

		if service.is_enabled():
			controls_control.append('[D]isable')
		else:
			controls_control.append('[E]nable')

		if service.game.multi_binary:
			if service.is_stopped():
				controls_control.append('[U]pdate')
			else:
				controls_control.append(f'{ESCAPE_STRIKE}[U]pdate{ESCAPE_RESET}')

		if 'create_service' in features:
			if service.is_stopped():
				controls_control.append('[REMOVE] service')
			else:
				controls_control.append(f'{ESCAPE_STRIKE}[REMOVE] service{ESCAPE_RESET}')

		if service.is_stopped():
			controls_data.append('[R]estore and Backup')
			controls_data.append('[W]ipe')
		else:
			controls_data.append(f'{ESCAPE_STRIKE}[R]estore and Backup{ESCAPE_RESET}')
			controls_data.append(f'{ESCAPE_STRIKE}[W]ipe{ESCAPE_RESET}')

		if len(controls_configure) > 0:
			print('Configure: ' + ' | '.join(controls_configure))
		print('Control: ' + ' | '.join(controls_control))
		if len(controls_data) > 0:
			print('Manage Data: ' + ' | '.join(controls_data))
		print('or [B]ack to menu / [Q]uit to exit')
		opt = input(': ').lower()

		if opt != 'q':
			os.system('clear')

		if opt.isdigit() and 1 <= int(opt) <= counter:
			if service.is_running():
				logger.warning('Cannot configure options for a service while it is running.')
			else:
				menu_config_option(service, options_ordered[int(opt) - 1])
		elif opt == 'b':
			return
		elif opt == 'd':
			service.disable()
		elif opt == 'e':
			service.enable()
		elif opt == 'm':
			menu_mods(service)
		elif opt == 'o':
			menu_config(service, other_options)
		elif opt == 'q':
			sys.exit(0)
		elif opt == 'r':
			if service.is_stopped():
				menu_backup(service)
		elif opt == 's':
			service.start()
		elif opt == 't':
			service.stop()
		elif opt == 'u':
			if service.is_stopped():
				service.update()
		elif opt == 'w':
			if service.is_stopped() and prompt_yn('Are you sure you want to wipe all data for this service?', default='n'):
				service.wipe()
		elif opt == 'remove':
			if service.is_stopped() and prompt_yn('Are you sure you want to remove this service?', default='n'):
				if prompt_yn('This will probably remove all player data for this service, continue?', default='n'):
					service.game.remove_service(service.service)
					return


def menu_public_auth(nexus: Nexus):
	"""
	Set the auth token for managing the public profile and managing hosts

	:return:
	"""
	global AUTH_TOKEN
	print_header('Log into Warlock.Nexus')
	while True:
		token = input('Enter your Warlock.Nexus auth token or [B]ack: ').strip()

		if token.lower() == 'b':
			nexus.user_auth = None
			return

		nexus.user_auth = token
		ret = nexus.community_ping()
		if ret['success']:
			# Cache this in memory for future use
			AUTH_TOKEN = token
			return
		else:
			print('')
			print(ret['message'])


def menu_public_email(nexus: Nexus):
	print_header('Set Email for Warlock.Nexus')
	while True:
		print('Please enter your email you used to subscribe on https://ko-fi.com/bitsandbytes')
		print('To go back, just press ENTER without changing your email.')
		print('')
		email = prompt_text('Email:', nexus.email, True)

		if email == nexus.email or email == '':
			return

		nexus.email = email
		# Try to perform a lookup to validate the email
		full_details = nexus.community_full()
		if full_details['success']:
			nexus.set_email(email)
			return
		else:
			print('')
			print(full_details['message'])
			print('')
			print('Could not validate email.  Please try again.')


def menu_public_hosts(nexus):
	while True:
		print_header('Registered Hosts')
		print('')
		print('Server hosts that are authorized to access mod data and publish public game metrics')
		print('')
		full_details = nexus.community_full()
		if not full_details['success']:
			print(full_details['message'])
			return

		table = Table(['#', 'IP', 'OS', 'Hostname', 'Region', 'Country'])
		hosts = []
		counter = 0
		for host in full_details['data']['hosts']:
			counter += 1
			table.add([
				counter,
				host['ip'],
				host['os'],
				host['hostname'],
				host['region'],
				host['country']
			])
			hosts.append(host['id'])

		if len(hosts) == 0:
			print('No registered hosts')
			print('')
			print('[R]egister this host | [B]ack to previous menu, [Q]uit to exit')
		else:
			table.render()
			print('')
			print('[1-%s] to unregister and revoke authorization on a host' % counter)
			if not full_details['data']['host_registered']:
				print('[R]egister this host')
			print('[B]ack to previous menu, [Q]uit to exit')
		opt = input(': ').lower()

		if opt == 'b':
			return
		elif opt.isdigit() and 1 <= int(opt) <= counter:
			host_id = hosts[int(opt) - 1]
			if prompt_yn('Are you sure you want to deregister this host?', default='n'):
				nexus.host_unregister(host_id)
		elif opt == 'q':
			sys.exit(0)
		elif opt == 'r':
			nexus.host_register()


def menu_public():
	nexus = Nexus()
	nexus.user_auth = AUTH_TOKEN

	if nexus.email is None:
		print('Public community profiles are available to monthly supporters')
		print(' at https://ko-fi.com/bitsandbytes')
		print('')
		print('A $6 monthly donation will allow you to create public profiles,')
		print(' access mod search and installation for select games')
		print(' and register up to 3 server hosts.')
		print('')
		print('Refer to https://warlock.nexus/pages/communities.html for currently posted communities.')
		print('')
		print('Once you sign up, enter the email you used on ko-fi or [ENTER] to go back')
		opt = input(': ')

		if opt.strip() == '':
			# Empty response; user opted to skip out
			return

		nexus.set_email(opt)

	while True:
		print_header('Public Community Profile')
		print('')
		print('This controls how your public profile appears on https://warlock.nexus, (if enabled)')
		print('')

		full_details = nexus.community_full()
		if not full_details['success']:
			loggedin = False
			print('')
			print(full_details['message'])
			print('')
			print('Could not retrieve community details!  Check that you set your email correctly')
			print(' and have a valid subscription on https://ko-fi.com/bitsandbytes')
		else:
			loggedin = nexus.user_auth is not None
			table = Table()

			if full_details['data']['expired']:
				membership_status = f'{ICON_DISABLED} Expired - renew at https://ko-fi.com/bitsandbytes'
			else:
				membership_status = f'{ICON_ENABLED} Active'
			table.add(['Membership Status', '', membership_status])

			table.add(['Expires', '', full_details['data']['expires']])

			if full_details['data']['locked']:
				public_status = f'{ICON_DISABLED} Administratively Locked (please contact support)'
			elif not full_details['data']['enabled']:
				public_status = f'{ICON_DISABLED} Disabled'
			else:
				public_status = f'{ICON_ENABLED} Enabled'
			table.add(['Public', '[1]' if loggedin else ICON_LOCKED, public_status])

			table.add([
				'Host Usage',
				'',
				'%s / %s' % (full_details['data']['current_hosts'], full_details['data']['max_hosts'])
			])
			for host in full_details['data']['hosts']:
				table.add([
					'Host %s' % host['ip'],
					'',
					'%s - %s - %s %s' % (host['os'], host['hostname'], host['region'], host['country'])
				])
			table.add([
				'Host Status',
				'',
				(ICON_ENABLED + ' Registered') if full_details['data']['host_registered'] else (ICON_DISABLED + ' Not Registered')
			])
			table.add(['Name', '[2]' if loggedin else ICON_LOCKED, full_details['data']['name']])
			table.add(['Tagline', '[3]' if loggedin else ICON_LOCKED, full_details['data']['tagline']])
			table.add(['Country', '[4]' if loggedin else ICON_LOCKED, full_details['data']['country']])
			table.add(['Color', '[5]' if loggedin else ICON_LOCKED, full_details['data']['color']])

			if len(full_details['data']['socials']):
				table.add(['Socials', '[6]' if loggedin else ICON_LOCKED, full_details['data']['socials'][0]])
				# Add the rest of them, sans the first two columns.
				for social in full_details['data']['socials'][1:]:
					table.add(['', '', social])

			if full_details['data']['description'] == '':
				desc = 'No description set'
			else:
				desc = 'Description set and %s characters long' % len(full_details['data']['description'])
			table.add(['Description', '[7]' if loggedin else ICON_LOCKED, desc])

			table.render()

		print('')
		if not full_details['success']:
			print('[E]mail change | [B]ack to previous menu, [Q]uit to exit')
		elif loggedin:
			print('[1-6] to edit | [E]mail change | [H]ost management | [B]ack to previous menu, [Q]uit to exit')
		else:
			print('[L]ogin to change values | [E]mail change | [B]ack to previous menu, [Q]uit to exit')
		opt = input(': ').lower()

		payload = None
		if loggedin and opt.isdigit() and int(opt) == 1:
			if full_details['data']['locked']:
				print('Cannot enable/disable as it is administratively locked.')
			else:
				payload = {
					'enabled': not full_details['data']['enabled']
				}
		elif loggedin and opt.isdigit() and int(opt) == 2:
			payload = {
				'name': prompt_text('Name: ', full_details['data']['name'], True)
			}
		elif loggedin and opt.isdigit() and int(opt) == 3:
			payload = {
				'tagline': prompt_text('Tagline: ', full_details['data']['tagline'], True)
			}
		elif loggedin and opt.isdigit() and int(opt) == 4:
			payload = {
				'country': prompt_text('Country: ', full_details['data']['country'], True)
			}
		elif loggedin and opt.isdigit() and int(opt) == 5:
			payload = {
				'color': prompt_text('Color: ', full_details['data']['color'], True)
			}
		elif loggedin and opt.isdigit() and int(opt) == 6:
			socials = '\n'.join(full_details['data']['socials'])
			socials = prompt_long_text('Enter social and web links, one on each line', socials).strip()
			payload = {
				'socials': socials.split('\n')
			}
		elif loggedin and opt.isdigit() and int(opt) == 7:
			payload = {
				'description': prompt_long_text('Description', full_details['data']['description'], '.md')
			}
		elif opt == 'b':
			return
		elif opt == 'e':
			menu_public_email(nexus)
		elif opt == 'h':
			menu_public_hosts(nexus)
		elif opt == 'l':
			menu_public_auth(nexus)
		elif opt == 'q':
			sys.exit(0)

		if payload is not None:
			# A payload was requested; handle that now.
			ret = nexus.community_patch(payload)
			if not ret['success']:
				print('')
				print(ret['message'])


def default_menu_main(game: BaseApp):
	features = game.features - game.disabled_features
	meta = get_meta()
	subtitles = []
	nexus = Nexus()

	if meta['url']:
		subtitles.append(meta['url'] + '\n')

	subtitles.append('Built with the Warlock Manager v%s' % meta['version'])
	subtitles.append('https://warlock.nexus')

	while True:
		running = game.is_active()
		services = game.get_services()
		print_header(
			'Welcome to the %s Server Manager' % game.desc,
			subtitle='\n'.join(subtitles)
		)
		table = Table(['#', 'Service', 'Name', 'Port', 'Auto-Start', 'Status', 'CPU', 'Mem', 'Players'])
		table.align = ['r', 'l', 'l', 'r', 'l', 'l', 'r', 'r', 'l']
		counter = 0
		for svc in services:
			# Push some metrics to Nexus if enabled.
			nexus.service_details(svc)

			counter += 1
			row = []
			for col in table.header:
				if col == '#':
					row.append(str(counter))
				else:
					row.append(stringify_value(col, svc))
			table.add(row)
		print('')
		table.render()

		controls_configure = []
		controls_control = []

		controls_configure.append('global [O]ptions')
		if 'create_service' in features:
			controls_configure.append('[C]reate Service')

		controls_configure.append('[P]ublic Data')

		controls_control.append('[S]tart all')
		controls_control.append('s[T]op all')
		controls_control.append('[R]estart all')
		if not game.multi_binary:
			if running:
				controls_control.append(f'{ESCAPE_STRIKE}[U]pdate{ESCAPE_RESET}')
			else:
				controls_control.append('[U]pdate')

		print('')
		print('1-%s to manage individual map settings' % len(services))
		print('Configure: ' + ' | '.join(controls_configure))
		print('Control: ' + ' | '.join(controls_control))
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
		elif opt == 'c':
			if 'create_service' in features:
				new_service = prompt_text('Enter the name of the service to create: ')
				if new_service:
					game.create_service(new_service)
		elif opt == 'o':
			menu_config(game, game.get_options())
		elif opt == 'p':
			menu_public()
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
				if prompt_yn('Are you sure you want to wipe all data for all services?', default='n'):
					if prompt_yn('This will delete ALL PLAYER DATA!!!! Continue?', default='n'):
						for service in game.get_services():
							service.wipe()
