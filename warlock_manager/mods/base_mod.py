import json
import logging
import os
from typing import TYPE_CHECKING

from warlock_manager.libs.download import download_file
from warlock_manager.libs import utils

if TYPE_CHECKING:
	from services.base_service import BaseService


class BaseMod:
	def __init__(self):
		self.name: str = ''
		"""
		Human-friendly name of this mod
		"""

		self.description: str | None = None
		"""
		Human-friendly description of this mod
		"""

		self.url: str | None = None
		"""
		Provider URL of this mod
		"""

		self.info_url: str | None = None
		"""
		Info URL of this mod, can be whatever the developer defined.
		"""

		self.icon: str | None = None
		"""
		Icon URL for this mod, must be fully resolved
		"""

		self.id: str | int | None = None
		"""
		Unique identifier for this mod set by the provider
		"""

		self.provider: str | None = None
		"""
		Provider of this mod, eg; 'curseforge'
		"""

		self.author: str | None = None
		"""
		Author name and/or contact info for the author of this mod
		"""

		self.source: str | None = None
		"""
		Source URL to download this mod
		"""

		self.version: str | None = None
		"""
		Version of this mod
		"""

		self.package: str | None = None
		"""
		Base package filename of this mod file, generally the source archive
		"""

		self.dependencies: list[str] | None = None
		"""
		List of mod dependencies
		"""

		self.files: dict[str, str] | None = None
		"""
		Dictionary of files installed in the game path

		Key is the source file, usually just '@',
		but can be '@:path/inside/zip' to extract a specific file from the source package.
		"""

	def to_dict(self) -> dict:
		"""
		Returns a dict representation of the mod.
		"""
		return {
			'name': self.name,
			'description': self.description,
			'url': self.url,
			'info_url': self.info_url,
			'icon': self.icon,
			'id': self.id,
			'provider': self.provider,
			'author': self.author,
			'source': self.source,
			'version': self.version,
			'package': self.package,
			'dependencies': self.dependencies,
			'files': self.files,
		}

	@classmethod
	def from_dict(cls, data: dict) -> 'BaseMod':
		"""
		Populate an object from a flat dictionary, (ie; that of generated from JSON)
		:param data:
		:return:
		"""
		mod = cls()
		for key, value in data.items():
			if key == 'files':
				# Check to ensure this is a dict, (previous versions used a simple list)
				if value is not None and not isinstance(value, dict):
					new_val = {}
					for file in value:
						new_val['@'] = file
					value = new_val
			setattr(mod, key, value)
		return mod

	def __str__(self):
		"""
		Returns a pretty string representation for pprint and print().
		"""
		return json.dumps(self.to_dict(), indent=4)

	def __repr__(self):
		return str(self)

	def __eq__(self, other):
		"""
		Compare this mod against another and check if they are the same

		:param other:
		:return:
		"""
		return self.name == other.name and self.id == other.id and self.version == other.version

	def is_same(self, other_mod: 'BaseMod') -> bool:
		"""
		Check if this mod is the same base mod as another, ignoring the version

		This is suitable in installation checks to see if the mod should be updated or installed.

		:param other_mod:
		:return:
		"""
		return self.provider == other_mod.provider and self.id == other_mod.id

	def calculate_files(self):
		"""
		Calculate the files in this mod that are to be installed.

		:return:
		"""
		# MUST be extended to do anything; each game has a different mod structure.
		pass

	def register(self):
		"""
		Register a mod by adding it to the registration file.

		Use a comparison key to ensure that the mod is only registered once.
		This key should be one of the properties under BaseMod which can be used to uniquely identify the mod.

		:return:
		"""
		registered_mods = self.get_registered_mods()
		for i in range(len(registered_mods)):
			mod = registered_mods[i]
			if mod == self:
				# Detected mod is the same as this one; replace the list.
				registered_mods[i] = self
				self.save_registered_mods(registered_mods)
				return

		# Mod not found, that's fine, just append it!
		registered_mods.append(self)
		self.save_registered_mods(registered_mods)

	def download(self) -> bool:
		"""
		Download this mod to the Packages cache

		Requires source and package to be set
		:return:
		"""

		if not self.source:
			logging.error('Mod install source not found!')
			return False

		if not self.package:
			logging.error('Mod install package not found!')
			return False

		target_archive = os.path.join(utils.get_app_directory(), 'Packages', self.package)
		if not os.path.exists(target_archive):
			download_file(self.source, target_archive)
		else:
			logging.debug('Mod already downloaded, skipping download')

		return True

	@classmethod
	def find_mods(cls, source: 'BaseService', mod_lookup: str) -> list['BaseMod']:
		"""
		Search for a mod manually added within Packages/

		:param source: Source game service to use for reference
		:param mod_lookup: Query text to lookup
		:return:
		"""
		mods = cls.get_registered_mods()
		search = mod_lookup.lower()
		ret = []
		for mod in mods:
			if search in mod.name.lower():
				ret.append(mod)
		return ret

	@classmethod
	def get_mod(cls, source: 'BaseService', provider: str | None, mod_id: str | int) -> 'BaseMod | None':
		"""
		Get a specific mod by ID, this only searches through manually-installed mods.

		:param source:   Source game service to use for reference
		:param provider: Mod provider, e.g. 'curseforge'
		:param mod_id:   Mod ID
		:return:
		"""
		mods = cls.get_registered_mods()
		for mod in mods:
			if mod.id == mod_id and mod.provider is None:
				return mod
		return None

	@classmethod
	def get_registered_mods(cls) -> list['BaseMod']:
		"""
		Get all registered mods, eg all mods which are present in the registration file
		:return:
		"""
		mods_path = os.path.join(utils.get_app_directory(), 'Packages', 'mods.json')
		if not os.path.exists(mods_path):
			# No mods installed; mods cache is empty.
			return []

		mods = []
		with open(mods_path, 'r') as f:
			raw_mods = json.load(f)

		for raw in raw_mods:
			mods.append(cls.from_dict(raw))

		return mods

	@classmethod
	def save_registered_mods(cls, mods: list['BaseMod']):
		"""
		Save the list of registered mods to the registration file

		:param mods:
		:return:
		"""
		mods_directory = os.path.join(utils.get_app_directory(), 'Packages')
		if not os.path.exists(mods_directory):
			utils.makedirs(mods_directory)

		mods_path = os.path.join(utils.get_app_directory(), 'Packages', 'mods.json')

		flat_mods = []
		for mod in mods:
			flat_mods.append(mod.to_dict())

		with open(mods_path, 'w') as f:
			json.dump(flat_mods, f, indent=4)

	def get_provider_title(self) -> str:
		if self.provider is None:
			return 'Manually Added'
		elif self.provider == 'curseforge':
			return 'CurseForge'
		else:
			return self.provider
