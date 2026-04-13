import logging
import os
import time

import requests
import hashlib
import secrets
from warlock_manager.libs.cmd import Cmd
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.utils import get_app_directory


class Nexus:
	def __init__(self):
		self.email_file = '/var/lib/warlock/.email'
		self.host_auth = None
		self.user_auth = None
		self.email = None
		self.base_url = 'https://api.warlock.nexus'
		self.game = None

		if os.path.exists('/var/lib/warlock/.auth'):
			with open('/var/lib/warlock/.auth', 'r') as f:
				self.host_auth = f.read().strip()
		else:
			# This shouldn't get hit in Production, but can be useful in testing.
			# Auto-generate a new auth token for this host.
			self.host_auth = secrets.token_hex(32)
			with open('/var/lib/warlock/.auth', 'w') as f:
				f.write(self.host_auth)

		if os.path.exists(self.email_file):
			with open(self.email_file, 'r') as f:
				self.email = f.read().strip()

		guid_path = os.path.join(get_app_directory(), '.warlock.guid')
		if os.path.exists(guid_path):
			with open(guid_path, 'r') as f:
				self.game = f.read().strip()

	def set_email(self, email: str):
		"""
		Set the email address of the user that has authenticated with Warlock.Nexus.

		:param email:
		:return:
		"""
		with open(self.email_file, 'w') as f:
			f.write(email)
		self.email = email

	def get_email_hash(self) -> str:
		"""
		Get the SHA256 hash of the user's email address.

		Warlock.Nexus doesn't use or store the user's email, instead it uses the SHA256 hash
		of the email address to identify the user.

		:return:
		"""
		if self.email is None:
			raise ValueError('Email not set')
		return hashlib.sha256(self.email.encode('utf-8')).hexdigest()

	def host_register(self) -> dict:
		"""
		Register this host with Warlock.Nexus

		Returns the response from the API which contains:

		* success (bool)
		* message (str)

		:see: https://api.warlock.nexus/api/#operation/5fc076653d604d3d9d62eaa885fb1f5e
		:return:
		"""
		headers = {
			'X-Email': self.get_email_hash(),
			'X-Host-Token': self.host_auth,
		}

		# Set additional authentication, required for adding more than one host
		if self.user_auth is not None:
			headers['X-Auth-Token'] = self.user_auth

		# Generate a payload about this host
		payload = {
			'os': Cmd(['lsb_release', '-ds']).text,
			'hostname': Cmd(['hostname', '-f']).text,
		}
		try:
			r = requests.post(self.base_url + '/host/register', headers=headers, json=payload)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def host_unregister(self, host_id: str) -> dict:
		"""
		Unregister a host from Warlock.Nexus

		Returns the response from the API which contains:

		* success (bool)
		* message (str)

		:see: https://api.warlock.nexus/api/#operation/5fc076653d604d3d9d62eaa885fb1f5e
		:return:
		"""
		if self.user_auth is None:
			return {
				'success': False,
				'message': 'User authentication token not set',
			}

		headers = {
			'X-Email': self.get_email_hash(),
			'X-Host-Token': self.host_auth,
			'X-Auth-Token': self.user_auth,
		}

		try:
			r = requests.post(self.base_url + '/host/unregister/' + host_id, headers=headers)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def community_full(self) -> dict:
		"""
		Get the full details of the membership community

		:see: https://api.warlock.nexus/api/#operation/930ea03a32fdb3f22fc43b0c915327a4
		:return:
		"""
		try:
			headers = {
				'X-Email': self.get_email_hash(),
				'X-Host-Token': self.host_auth,
			}
		except ValueError as e:
			return {
				'success': False,
				'message': str(e),
			}

		try:
			r = requests.get(self.base_url + '/community/full', headers=headers)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def community_ping(self) -> dict:
		"""
		Perform a NOOP request to test authentication parameters

		:see: https://api.warlock.nexus/api/#operation/50960a7ec120982ae834ab9abfb919b0
		:return:
		"""
		headers = {
			'X-Email': self.get_email_hash(),
			'X-Auth-Token': self.user_auth,
		}

		try:
			r = requests.get(self.base_url + '/community/ping', headers=headers)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def community_patch(self, payload: dict) -> dict:
		"""
		Send a PATCH request to update the community profile

		:param payload:
		:return:
		"""
		if self.user_auth is None:
			return {
				'success': False,
				'message': 'User authentication token not set',
			}

		headers = {
			'X-Email': self.get_email_hash(),
			'X-Auth-Token': self.user_auth,
		}
		try:
			r = requests.patch(self.base_url + '/community/details', headers=headers, json=payload)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def service_details(self, service: BaseService):
		"""
		Push service details to Warlock.Nexus

		:see: https://api.warlock.nexus/api/#operation/4f248b2e4f1acc2eea21392a49ae6f6b
		:param service:
		:return:
		"""
		if not self.email:
			# If the email is not set, do not try to push stats, (this host probably is not authorized to send)
			return

		if not service.is_running():
			# Only push stats for running services
			return

		last_checkin_file = os.path.join(get_app_directory(), '.cache', '.%s.checkin' % service.service)
		now = int(time.time())
		if os.path.exists(last_checkin_file):
			# Only push stats once every 15 minutes
			with open(last_checkin_file, 'r') as f:
				last_checkin = int(f.read().strip())
			if last_checkin + (15 * 60) >= now:
				return

		mods = service.get_enabled_mods()
		mod_info = []
		for mod in mods:
			mod_info.append({
				'name': mod.name,
				'url': mod.url,
			})
		headers = {
			'X-Host-Token': self.host_auth,
		}
		payload = {
			'service': service.service,
			'address': '%s:%s' % (service.get_ip(), service.get_port()) if service.get_port() else service.get_ip(),
			'game': self.game,
			'players': service.get_player_count() or 0,
			'players_max': service.get_player_max() or 0,
			'day': 0,  # @todo
			'mods': mod_info,
			'password': False,  # @todo
			'name': service.get_name(),
		}

		# This request is meant to run in the background very quickly and we don't really care about the response.
		try:
			requests.post(self.base_url + '/service/details', headers=headers, json=payload, timeout=1)
			# Record the last time this service recorded metrics
			with open(last_checkin_file, 'w') as f:
				f.write(str(now))
		except requests.exceptions.RequestException as e:
			logging.debug('Error pushing service details: %s' % str(e))

	def mod_search(self, query: str, version: str | None, loader: str | None):
		"""
		Search Warlock.Nexus for a given mod

		:param query:   Search query
		:param version: Version of the game to limit results to, (if supported)
		:param loader:  Launcher of the game to limit results to, (if supported)
		:return:
		"""
		headers = {
			'X-Host-Token': self.host_auth,
		}

		try:
			url = self.base_url + '/mod/search/' + self.game
			params = {
				'query': query
			}
			if version is not None:
				params['version'] = version
			if loader is not None:
				params['loader'] = loader
			r = requests.get(url, headers=headers, params=params)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}

	def mod_get(self, provider: str, mod_id: str | int, version: str | None, loader: str | None):
		"""
		Get a specific mod metadata from Warlock.Nexus

		:param provider: Mod provider, e.g. 'curseforge'
		:param mod_id:   Mod ID
		:param version:  Version of the game to limit results to, (if supported)
		:param loader:   Launcher of the game to limit results to, (if supported)
		:return:
		"""
		headers = {
			'X-Host-Token': self.host_auth,
		}

		try:
			url = self.base_url + '/mod/get/' + self.game + '/' + provider + '/' + mod_id
			params = {}
			if version is not None:
				params['version'] = version
			if loader is not None:
				params['loader'] = loader
			r = requests.get(url, headers=headers, params=params)
			return r.json()
		except requests.exceptions.RequestException as e:
			return {
				'success': False,
				'message': str(e),
			}
