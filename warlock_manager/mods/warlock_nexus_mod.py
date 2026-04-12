import logging
from typing import TYPE_CHECKING

from warlock_manager.nexus.nexus import Nexus
from warlock_manager.mods.base_mod import BaseMod
if TYPE_CHECKING:
	from warlock_manager.services.base_service import BaseService


class WarlockNexusMod(BaseMod):

	@classmethod
	def find_mods(cls, source: 'BaseService', mod_lookup: str) -> list['WarlockNexusMod']:
		"""
		Search for a mod via Warlock.Nexus, must be a sponsor to use this.

		:param source: Source game service to use for reference
		:param mod_lookup: Query text to lookup
		:return:
		"""
		nexus = Nexus()
		ret = []
		result = nexus.mod_search(mod_lookup, source.get_version(), source.get_loader())
		if not result['success']:
			logging.error('Failed to search for mods: %s' % result['message'])
			return ret

		for data in result['data']:
			mod = WarlockNexusMod()
			mod.id = data['id']
			mod.name = data['name']
			mod.url = data['url']
			mod.description = data['description']
			mod.icon = data['icon']
			mod.author = data['author']
			mod.source = data['source']
			mod.version = data['version']
			mod.package = data['package']
			mod.dependencies = data['dependencies']
			ret.append(mod)

		return ret

	@classmethod
	def get_mod(cls, source: 'BaseService', mod_id: str) -> 'WarlockNexusMod | None':
		"""
		Get a specific mod by ID, must be a sponsor to use this.

		:param mod_id:
		:return:
		"""
		nexus = Nexus()
		result = nexus.mod_get(mod_id, source.get_version(), source.get_loader())
		if not result['success']:
			logging.error('Failed to get mod: %s' % result['message'])
			return None

		data = result['data']
		mod = WarlockNexusMod()
		mod.id = data['id']
		mod.name = data['name']
		mod.url = data['url']
		mod.description = data['description']
		mod.icon = data['icon']
		mod.author = data['author']
		mod.source = data['source']
		mod.version = data['version']
		mod.package = data['package']
		mod.dependencies = data['dependencies']

		return mod
