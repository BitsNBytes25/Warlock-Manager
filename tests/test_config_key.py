import unittest
from warlock_manager.config.config_key import ConfigKey


class TestConfigKey(unittest.TestCase):
	def test_default_bool(self):
		self.assertTrue(ConfigKey.from_dict({'type': 'bool', 'default': 'True'}).default)
		self.assertTrue(ConfigKey.from_dict({'type': 'bool', 'default': '1'}).default)
		self.assertTrue(ConfigKey.from_dict({'type': 'bool', 'default': 'yes'}).default)
		self.assertFalse(ConfigKey.from_dict({'type': 'bool', 'default': 'false'}).default)
		self.assertFalse(ConfigKey.from_dict({'type': 'bool', 'default': '0'}).default)

	def test_type_bool(self):
		key = ConfigKey.from_dict({'type': 'bool'})
		self.assertTrue(isinstance(key, ConfigKey))
		self.assertTrue(key.to_system_type(True))
		self.assertTrue(key.to_system_type('True'))
		self.assertTrue(key.to_system_type('yes'))
		self.assertTrue(key.to_system_type('1'))

		self.assertFalse(key.to_system_type(False))
		self.assertFalse(key.to_system_type('False'))
		self.assertFalse(key.to_system_type('no'))
		self.assertFalse(key.to_system_type('0'))

	def test_type_int(self):
		key = ConfigKey.from_dict({'type': 'int'})
		self.assertTrue(isinstance(key, ConfigKey))
		self.assertEqual(123, key.to_system_type('123'))
		self.assertEqual(-456, key.to_system_type('-456'))
		self.assertEqual(0, key.to_system_type('0'))
		self.assertEqual(0, key.to_system_type(''))  # Empty string should defer to default, which is 0 for int
		self.assertEqual(3, key.to_system_type(3.14159))

	def test_type_float(self):
		key = ConfigKey.from_dict({'type': 'float'})
		self.assertTrue(isinstance(key, ConfigKey))
		self.assertEqual(3.14, key.to_system_type('3.14'))
		self.assertEqual(-2.718, key.to_system_type('-2.718'))
		self.assertEqual(0.0, key.to_system_type('0.0'))

	def test_type_str(self):
		key = ConfigKey.from_dict({'type': 'str'})
		self.assertTrue(isinstance(key, ConfigKey))
		self.assertEqual('Hello, World!', key.to_system_type('Hello, World!'))
		self.assertEqual('', key.to_system_type(''))

	def test_type_list(self):
		key = ConfigKey.from_dict({'type': 'list'})
		self.assertTrue(isinstance(key, ConfigKey))
		self.assertEqual(['a', 'b', 'c'], key.to_system_type('a,b,c'))
		self.assertEqual([], key.to_system_type(''))
