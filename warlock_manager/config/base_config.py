import os
import sys
from typing import Union
import yaml
from abc import ABC
from warlock_manager.config.config_key import ConfigKey, config_types


class BaseConfig(ABC):
	def __init__(self, group_name: str, *args, **kwargs):
		self.options = {}
		"""
		:type dict<str, tuple<str, str, str, str, str>>
		Primary dictionary of all options on this config

		* Item 0: Section
		* Item 1: Key
		* Item 2: Default Value
		* Item 3: Type (str, int, bool)
		* Item 4: Help Text
		"""

		self._keys = {}
		"""
		:type dict<str, str>
		Map of lowercase option keys to name for quick lookup
		"""

		# Load the configuration definitions from configs.yaml
		here = os.path.dirname(os.path.realpath(sys.argv[0]))

		if os.path.exists(os.path.join(here, 'configs.yaml')):
			with open(os.path.join(here, 'configs.yaml'), 'r') as cfgfile:
				cfgdata = yaml.safe_load(cfgfile)
				for cfgname, cfgoptions in cfgdata.items():
					if cfgname == group_name:
						for option in cfgoptions:
							self.add_option(option)

	def add_option(self, option_dict: dict):
		"""
		Add a configuration option to the available list

		:param name:
		:param section:
		:param key:
		:param default:
		:param val_type:
		:param help_text:
		:return:
		"""

		key = ConfigKey.from_dict(option_dict)
		self.options[key.name] = key
		# Primary dictionary of all options on this config

		self._keys[key.key.lower()] = key.name
		# Map of lowercase option names to sections for quick lookup

	def from_system_type(self, name: str, value: config_types) -> Union[str, list]:
		"""
		Convert a system type value to a string for storage
		:param name:
		:param value:
		:return:
		"""
		opt = self.get_config(name)
		if opt is None:
			print('Invalid option: %s, not available in configuration!' % (name, ), file=sys.stderr)
			return ''

		if opt.val_type == 'bool':
			if value == '':
				# Allow empty values to defer to default
				return ''
			elif value is True or (str(value).lower() in ('1', 'true', 'yes', 'on')):
				return 'True'
			else:
				return 'False'
		elif opt.val_type == 'list':
			if isinstance(value, list):
				return value
			else:
				# Assume comma-separated string
				return [item.strip() for item in str(value).split(',')]
		elif opt.val_type == 'float':
			# Unreal likes floats to be stored with 6 decimal places
			return f'{float(value):.6f}'
		else:
			return str(value)

	def get_value(self, name: str) -> Union[str, int, bool]:
		"""
		Get a configuration option from the config

		:param name: Name of the option
		:return:
		"""
		pass

	def set_value(self, name: str, value: Union[str, int, bool]):
		"""
		Set a configuration option in the config

		:param name: Name of the option
		:param value: Value to save
		:return:
		"""
		pass

	def has_value(self, name: str) -> bool:
		"""
		Check if a configuration option has been set

		:param name: Name of the option
		:return:
		"""
		pass

	def get_config(self, name: str) -> ConfigKey | None:
		"""
		Get the raw configuration key object for the given name, or None if not found

		:param name:
		:return:
		"""
		if name in self.options:
			return self.options[name]
		else:
			return None

	def get_default(self, name: str) -> config_types:
		"""
		Get the default value of a configuration option
		:param name:
		:return:
		"""
		opt = self.get_config(name)
		if opt is None:
			print('Invalid option: %s, not available in configuration!' % (name, ), file=sys.stderr)
			return ''

		return opt.to_system_type(opt.default)

	def get_type(self, name: str) -> str:
		"""
		Get the type of a configuration option from the config

		:param name:
		:return:
		"""
		opt = self.get_config(name)
		if opt is None:
			print('Invalid option: %s, not available in configuration!' % (name, ), file=sys.stderr)
			return ''

		return opt.val_type

	def get_help(self, name: str) -> str:
		"""
		Get the help text of a configuration option from the config

		:param name:
		:return:
		"""
		opt = self.get_config(name)
		if opt is None:
			print('Invalid option: %s, not available in configuration!' % (name, ), file=sys.stderr)
			return ''

		return opt.help

	def get_options(self, name: str):
		"""
		Get the list of valid options for a configuration option from the config

		:param name:
		:return:
		"""
		opt = self.get_config(name)
		if opt is None:
			print('Invalid option: %s, not available in configuration!' % (name, ), file=sys.stderr)
			return None

		return opt.options

	def exists(self) -> bool:
		"""
		Check if the config file exists on disk
		:return:
		"""
		pass

	def load(self, *args, **kwargs):
		"""
		Load the configuration file from disk
		:return:
		"""
		pass

	def save(self, *args, **kwargs):
		"""
		Save the configuration file back to disk
		:return:
		"""
		pass
