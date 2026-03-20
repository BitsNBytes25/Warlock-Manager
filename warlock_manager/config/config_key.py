config_types = str | int | bool | list | float


class ConfigKey:
	"""
	Configuration item for a single key.

	Pulled automatically from the configuration file `configs.yaml`.
	"""

	def __init__(self):
		self.name: str
		self.key: str = ''
		self.section: str | None = None
		self.default: config_types | None = None
		self.val_type: str = 'str'
		self.help: str = ''
		self.options: list | None = None
		self.group: str = 'Options'

	@classmethod
	def from_dict(cls, option):
		"""
		Instantiate a new ConfigKey based off a YAML object definition.

		:param option: dict
		:return: ConfigKey
		"""
		key = cls()

		key.name = option.get('name')
		key.key = option.get('key')
		key.section = option.get('section', None)
		key.val_type = option.get('type', 'str')
		key.default = key.to_system_type(option.get('default', None))
		key.help = option.get('help', '')
		key.options = option.get('options', None)
		key.group = option.get('group', 'Options')

		return key

	def to_system_type(self, value) -> config_types:
		"""
		Convert a string value to the appropriate system type based on this key's val_type
		:param value:
		:return:
		"""
		# Auto convert
		if self.val_type == 'int':
			if value is None or value == '':
				return 0
			return int(value)
		elif self.val_type == 'float':
			if value is None:
				return 0.0
			return float(value)
		elif self.val_type == 'bool':
			if isinstance(value, bool):
				return value
			elif value is None:
				return False
			return value.lower() in ('1', 'true', 'yes', 'on')
		elif self.val_type == 'list':
			if isinstance(value, list):
				return value
			elif value == '':
				return []
			else:
				# Assume comma-separated string
				return [item.strip() for item in str(value).split(',')]
		else:
			return value
