from typing import TYPE_CHECKING

from warlock_manager.nexus.nexus import Nexus
from warlock_manager.mods.base_mod import BaseMod
from warlock_manager.libs.logger import logger
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
		ret = []

		# Search local mods first, to retain support for manually-installed packages
		mods = cls.get_registered_mods()
		search = mod_lookup.lower()
		for mod in mods:
			if search in mod.name.lower():
				ret.append(mod)

		# Search Warlock.Nexus for multiple providers
		nexus = Nexus()
		result = nexus.mod_search(mod_lookup, source.get_version(), source.get_loader())
		if not result['success']:
			logger.error('Failed to search for mods: %s' % result['message'])
			return ret

		for data in result['data']:
			ret.append(cls.from_dict(data))

		return ret

	@classmethod
	def get_mod(cls, source: 'BaseService', provider: str | None, mod_id: str | int) -> 'WarlockNexusMod | None':
		"""
		Get a specific mod by ID, must be a sponsor to use this.

		:param source:   Source game service to use for reference
		:param provider: Mod provider, e.g. 'curseforge'
		:param mod_id:   Mod ID
		:return:
		"""
		if provider is None:
			# Search through local mods
			mods = cls.get_registered_mods()
			for mod in mods:
				if mod.id == mod_id and mod.provider is None:
					return mod
			return None

		nexus = Nexus()
		result = nexus.mod_get(provider, mod_id, source.get_version(), source.get_loader())
		if not result['success']:
			logger.error('Failed to get mod: %s' % result['message'])
			return None

		return cls.from_dict(result['data'])
