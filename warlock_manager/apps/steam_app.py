import os
import re
import sys
import time
import subprocess
from abc import ABC
from typing import Union

from .base_app import BaseApp


def guess_steamcmd_path() -> str:
	# Try to find steamcmd in the common locations
	paths = (
		'/usr/games/steamcmd',
		'/usr/local/games/steamcmd',
		'/opt/steamcmd/steamcmd.sh',
		'/usr/bin/steamcmd',
		'/usr/local/bin/steamcmd'
	)
	for path in paths:
		if os.path.exists(path):
			return path
	raise FileNotFoundError('steamcmd not found in common locations. Please ensure steamcmd is installed.')


def steamcmd_get_app_details(app_id: str) -> Union[dict, None]:
	"""
	Get detailed information about a Steam app using steamcmd

	Returns a dictionary with:

	- common
		- name
		- type
		- parent
		- ReleaseState
		- oslist
		- osarch
		- osextended
		- icon
		- clienticon
		- clienttga
		- freetodownload
		- associations
		- gameid
	- extended
		- gamedir
	- config
		- installdir
		- launch
		- uselaunchcommandline
	- depots

	:param app_id:
	:param steamcmd_path:
	:return:
	"""

	# Construct the command to get app details
	command = [
		guess_steamcmd_path(),
		"+login", "anonymous",
		"+app_info_update", "1",
		"+app_info_print", str(app_id),
		"+quit"
	]

	try:
		# Run the steamcmd command
		result = subprocess.run(command, capture_output=True, text=True, check=True)

		# Output from command should be Steam manifest format, parse it
		dat = steamcmd_parse_manifest(result.stdout)
		if app_id in dat:
			return dat[app_id]
		else:
			print(f"App ID {app_id} not found in steamcmd output.", file=sys.stderr)
			return None

	except subprocess.CalledProcessError as e:
		print(f"Error running steamcmd: {e}")
		return None


def steamcmd_parse_manifest(manifest_content):
	"""
	Parses a SteamCMD manifest file content and returns a dictionary
	with the all the relevant information.

	Example format of content to parse:

	"2131400"
	{
		"common"
		{
			"name"		"VEIN Dedicated Server"
			"type"		"Tool"
			"parent"		"1857950"
			"ReleaseState"		"released"
			"oslist"		"windows,linux"
			"osarch"		"64"
			"osextended"		""
			"icon"		"7573f431d9ecd0e9dc21f4406f884b92152508fd"
			"clienticon"		"b5de75f7c5f84027200fdafe0483caaeb80f7dbe"
			"clienttga"		"6012ea81d68607ad0dfc5610e61f17101373c1fd"
			"freetodownload"		"1"
			"associations"
			{
			}
			"gameid"		"2131400"
		}
		"extended"
		{
			"gamedir"		""
		}
		"config"
		{
			"installdir"		"VEIN Dedicated Server"
			"launch"
			{
				"0"
				{
					"executable"		"VeinServer.exe"
					"type"		"default"
					"config"
					{
						"oslist"		"windows"
					}
					"description_loc"
					{
						"english"		"VEIN Dedicated Server"
					}
					"description"		"VEIN Dedicated Server"
				}
				"1"
				{
					"executable"		"VeinServer.sh"
					"type"		"default"
					"config"
					{
						"oslist"		"linux"
					}
					"description_loc"
					{
						"english"		"VEIN Dedicated Server"
					}
					"description"		"VEIN Dedicated Server"
				}
			}
			"uselaunchcommandline"		"1"
		}
		"depots"
		{
			"228989"
			{
				"config"
				{
					"oslist"		"windows"
				}
				"depotfromapp"		"228980"
				"sharedinstall"		"1"
			}
			"228990"
			{
				"config"
				{
					"oslist"		"windows"
				}
				"depotfromapp"		"228980"
				"sharedinstall"		"1"
			}
			"2131401"
			{
				"config"
				{
					"oslist"		"windows"
				}
				"manifests"
				{
					"public"
					{
						"gid"		"3422721066391688500"
						"size"		"13373528354"
						"download"		"4719647568"
					}
					"experimental"
					{
						"gid"		"5376672931011513884"
						"size"		"14053570688"
						"download"		"4881399680"
					}
				}
			}
			"2131402"
			{
				"config"
				{
					"oslist"		"linux"
				}
				"manifests"
				{
					"public"
					{
						"gid"		"4027172715479418364"
						"size"		"14134939630"
						"download"		"4869512928"
					}
					"experimental"
					{
						"gid"		"643377871134354986"
						"size"		"14712396815"
						"download"		"4982816608"
					}
				}
			}
			"branches"
			{
				"public"
				{
					"buildid"		"20727232"
					"timeupdated"		"1762674215"
				}
				"experimental"
				{
					"buildid"		"20729593"
					"description"		"Bleeding-edge updates"
					"timeupdated"		"1762704776"
				}
			}
			"privatebranches"		"1"
		}
	}

	:param manifest_content: str, content of the SteamCMD manifest file
	:return: dict, parsed manifest data
	"""
	lines = manifest_content.splitlines()
	stack = []
	current_dict = {}
	current_key = None

	for line in lines:
		line = line.strip()
		if line == '{':
			new_dict = {}
			if current_key is not None:
				current_dict[current_key] = new_dict
			stack.append((current_dict, current_key))
			current_dict = new_dict
			current_key = None
		elif line == '}':
			if stack:
				current_dict, current_key = stack.pop()
		else:
			match = re.match(r'"(.*?)"\s*"(.*?)"', line)
			if match:
				key, value = match.groups()
				current_dict[key] = value
			else:
				match = re.match(r'"(.*?)"', line)
				if match:
					current_key = match.group(1)

	return current_dict


def steamcmd_check_app_update(app_manifest: str):
	if not os.path.exists(app_manifest):
		print(f"App manifest file {app_manifest} does not exist.", file=sys.stderr)
		return False

	# App manifest is a local copy of the app JSON data
	with open(app_manifest, 'r') as f:
		details = steamcmd_parse_manifest(f.read())

	if 'AppState' not in details:
		print(f"Invalid app manifest format in {app_manifest}.", file=sys.stderr)
		return False

	# Pull local data about the installed game from its manifest file
	app_id = details['AppState']['appid']
	build_id = details['AppState']['buildid']

	if 'MountedConfig' in details['AppState'] and 'BetaKey' in details['AppState']['MountedConfig']:
		branch = details['AppState']['MountedConfig']['BetaKey']
	else:
		branch = 'public'

	# Pull the latest app details from SteamCMD
	details = steamcmd_get_app_details(app_id)

	# Ensure some basic data integrity
	if 'depots' not in details:
		print(f"No depot information found for app {app_id}.", file=sys.stderr)
		return False

	if 'branches' not in details['depots']:
		print(f"No branch information found for app {app_id}.", file=sys.stderr)
		return False

	if branch not in details['depots']['branches']:
		print(f"Branch {branch} not found for app {app_id}.", file=sys.stderr)
		return False

	# Just check if the build IDs differ
	available_build_id = details['depots']['branches'][branch]['buildid']
	return build_id != available_build_id


class SteamApp(BaseApp, ABC):
	"""
	Game application manager
	"""

	def __init__(self):
		super().__init__()
		self.steam_id = ''
		self.steam_branch = 'public'
		self.steam_branch_password = ''

	def check_update_available(self) -> bool:
		"""
		Check if a SteamCMD update is available for this game

		:return:
		"""
		here = os.path.dirname(os.path.realpath(sys.argv[0]))
		return steamcmd_check_app_update(os.path.join(here, 'AppFiles', 'steamapps', 'appmanifest_%s.acf' % self.steam_id))

	def update(self):
		"""
		Update the game server via SteamCMD

		:return:
		"""
		# Stop any running services before updating
		services = []
		for service in self.get_services():
			if service.is_running() or service.is_starting():
				print('Stopping service %s for update...' % service.service)
				services.append(service.service)
				subprocess.Popen(['systemctl', 'stop', service.service])

		if len(services) > 0:
			# Wait for all services to stop, may take 5 minutes if players are online.
			print('Waiting up to 5 minutes for all services to stop...')
			counter = 0
			while counter < 30:
				all_stopped = True
				counter += 1
				for service in self.get_services():
					if service.is_running() or service.is_starting() or service.is_stopping():
						all_stopped = False
						break
				if all_stopped:
					break
				time.sleep(10)
		else:
			print('No running services found, proceeding with update...')

		here = os.path.dirname(os.path.realpath(sys.argv[0]))
		cmd = [
			guess_steamcmd_path(),
			'+force_install_dir',
			os.path.join(here, 'AppFiles'),
			'+login',
			'anonymous',
			'+app_update',
			self.steam_id,
		]

		if self.steam_branch != 'public':
			cmd.append('-beta')
			cmd.append(self.steam_branch)
			if self.steam_branch_password != '':
				cmd.append('-betapassword')
				cmd.append(self.steam_branch_password)

		cmd.append('validate')
		cmd.append('+quit')

		if os.geteuid() == 0:
			stat_info = os.stat(here)
			uid = stat_info.st_uid
			cmd = [
				'sudo',
				'-u',
				'#%s' % uid
			] + cmd

		res = subprocess.run(cmd)

		# Allow the game to perform any post-update tasks
		self.post_update()

		if len(services) > 0:
			print('Update completed, restarting previously running services...')
			for service in services:
				subprocess.Popen(['systemctl', 'start', service])
				time.sleep(10)

		return res.returncode == 0
