import os
import shutil
import tempfile
import unittest

from warlock_manager.config.ini_config import INIConfig

here = os.path.dirname(os.path.realpath(__file__))


class TestINIConfig(unittest.TestCase):
	"""Test cases for INIConfig class"""

	def test_init(self):
		"""Test basic initialization of INIConfig"""
		cfg = INIConfig('test_group', '/tmp/test.ini')
		self.assertIsInstance(cfg.options, dict)
		self.assertEqual(cfg.path, '/tmp/test.ini')
		self.assertEqual(cfg.group, 'test_group')
		self.assertFalse(cfg.spoof_group)
		self.assertIsNotNone(cfg.parser)

	def test_exists_false(self):
		"""Test exists() returns False for non-existent file"""
		cfg = INIConfig('test', '/tmp/nonexistent_test_file_xyz123.ini')
		self.assertFalse(cfg.exists())

	def test_exists_true(self):
		"""Test exists() returns True for existing file"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		self.assertTrue(cfg.exists())

	def test_load_and_get_value_string(self):
		"""Test loading config and retrieving string values"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'StringKey',
			'section': 'TestSection',
			'key': 'StringKey',
		})
		cfg.load()

		value = cfg.get_value('StringKey')
		self.assertEqual(value, 'TestValue')

	def test_load_and_get_value_int(self):
		"""Test loading config and retrieving integer values"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'IntKey',
			'section': 'TestSection',
			'key': 'IntKey',
			'type': 'int'
		})
		cfg.load()

		value = cfg.get_value('IntKey')
		self.assertEqual(value, 100)
		self.assertIsInstance(value, int)

	def test_load_and_get_value_bool(self):
		"""Test loading config and retrieving boolean values"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'BoolKey',
			'section': 'TestSection',
			'key': 'BoolKey',
			'type': 'bool'
		})
		cfg.load()

		value = cfg.get_value('BoolKey')
		self.assertEqual(value, True)
		self.assertIsInstance(value, bool)

	def test_get_value_missing_option(self):
		"""Test get_value() returns empty string for invalid option"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.load()

		# Getting a value for an option that wasn't added should return empty string
		value = cfg.get_value('NonExistentOption')
		self.assertEqual(value, '')

	def test_get_value_missing_section(self):
		"""Test get_value() returns default when section is missing"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'TestKey',
			'section': 'NonExistentSection',
			'key': 'TestKey',
			'default': 'DefaultValue'
		})
		cfg.load()

		value = cfg.get_value('TestKey')
		self.assertEqual(value, 'DefaultValue')

	def test_get_value_missing_key(self):
		"""Test get_value() returns default when key is missing from section"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'TestKey',
			'section': 'TestSection',
			'key': 'NonExistentKey',
			'default': 'FallbackValue'
		})
		cfg.load()

		value = cfg.get_value('TestKey')
		self.assertEqual(value, 'FallbackValue')

	def test_has_value_exists(self):
		"""Test has_value() returns True for existing values"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'StringKey',
			'section': 'TestSection',
			'key': 'StringKey',
		})
		cfg.load()

		self.assertTrue(cfg.has_value('StringKey'))

	def test_has_value_does_not_exist(self):
		"""Test has_value() returns False for non-existent values"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'NonExistentKey',
			'section': 'TestSection',
			'key': 'NonExistentKey',
		})
		cfg.load()

		self.assertFalse(cfg.has_value('NonExistentKey'))

	def test_has_value_missing_section(self):
		"""Test has_value() returns False when section doesn't exist"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'TestKey',
			'section': 'NonExistentSection',
			'key': 'TestKey',
		})
		cfg.load()

		self.assertFalse(cfg.has_value('TestKey'))

	def test_has_value_invalid_option(self):
		"""Test has_value() returns False for invalid option names"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.load()

		self.assertFalse(cfg.has_value('NonRegisteredOption'))

	def test_set_value_and_save(self):
		"""Test setting a value and saving to file"""
		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.ini')
			shutil.copyfile(
				os.path.join(here, 'data', 'test_ini_simple.ini'),
				path
			)

			cfg = INIConfig('test', path)
			cfg.add_option({
				'name': 'StringKey',
				'section': 'TestSection',
				'key': 'StringKey',
			})
			cfg.load()

			# Verify initial value
			self.assertEqual(cfg.get_value('StringKey'), 'TestValue')

			# Set new value
			cfg.set_value('StringKey', 'NewValue')
			self.assertEqual(cfg.get_value('StringKey'), 'NewValue')

			# Save and reload to verify persistence
			cfg.save()
			cfg2 = INIConfig('test', path)
			cfg2.add_option({
				'name': 'StringKey',
				'section': 'TestSection',
				'key': 'StringKey',
			})
			cfg2.load()
			self.assertEqual(cfg2.get_value('StringKey'), 'NewValue')

	def test_set_value_creates_new_section(self):
		"""Test set_value() creates section if it doesn't exist"""
		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.ini')
			shutil.copyfile(
				os.path.join(here, 'data', 'test_ini_simple.ini'),
				path
			)

			cfg = INIConfig('test', path)
			cfg.add_option({
				'name': 'NewKey',
				'section': 'NewSection',
				'key': 'NewKey',
			})
			cfg.load()

			# Set value in non-existent section
			cfg.set_value('NewKey', 'NewValue')
			self.assertEqual(cfg.get_value('NewKey'), 'NewValue')

			# Save and verify
			cfg.save()
			with open(path, 'r') as f:
				content = f.read()
			self.assertIn('[NewSection]', content)
			self.assertIn('newkey', content.lower())
			self.assertIn('newvalue', content.lower())

	def test_set_value_with_percent_escaping(self):
		"""Test set_value() properly escapes percent characters"""
		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.ini')
			shutil.copyfile(
				os.path.join(here, 'data', 'test_ini_simple.ini'),
				path
			)

			cfg = INIConfig('test', path)
			cfg.add_option({
				'name': 'PercentKey',
				'section': 'TestSection',
				'key': 'PercentKey',
			})
			cfg.load()

			# Set value with percent characters
			cfg.set_value('PercentKey', 'Value%with%percent')
			cfg.save()

			# Reload and verify value is restored correctly
			cfg2 = INIConfig('test', path)
			cfg2.add_option({
				'name': 'PercentKey',
				'section': 'TestSection',
				'key': 'PercentKey',
			})
			cfg2.load()
			self.assertEqual(cfg2.get_value('PercentKey'), 'Value%with%percent')

	def test_set_value_all_types(self):
		"""Test set_value() with string, int, and bool types"""
		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.ini')
			shutil.copyfile(
				os.path.join(here, 'data', 'test_ini_simple.ini'),
				path
			)

			cfg = INIConfig('test', path)
			cfg.add_option({
				'name': 'StrVal',
				'section': 'TestSection',
				'key': 'StrVal',
				'type': 'str'
			})
			cfg.add_option({
				'name': 'IntVal',
				'section': 'TestSection',
				'key': 'IntVal',
				'type': 'int'
			})
			cfg.add_option({
				'name': 'BoolVal',
				'section': 'TestSection',
				'key': 'BoolVal',
				'type': 'bool'
			})
			cfg.load()

			# Set values
			cfg.set_value('StrVal', 'MyString')
			cfg.set_value('IntVal', 42)
			cfg.set_value('BoolVal', True)
			cfg.save()

			# Reload and verify
			cfg2 = INIConfig('test', path)
			cfg2.add_option({'name': 'StrVal', 'section': 'TestSection', 'key': 'StrVal', 'type': 'str'})
			cfg2.add_option({'name': 'IntVal', 'section': 'TestSection', 'key': 'IntVal', 'type': 'int'})
			cfg2.add_option({'name': 'BoolVal', 'section': 'TestSection', 'key': 'BoolVal', 'type': 'bool'})
			cfg2.load()

			self.assertEqual(cfg2.get_value('StrVal'), 'MyString')
			self.assertEqual(cfg2.get_value('IntVal'), 42)
			self.assertEqual(cfg2.get_value('BoolVal'), True)

	def test_set_value_missing_option(self):
		"""Test set_value() with invalid option prints error"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.load()

		# Trying to set a value for an unregistered option should do nothing
		cfg.set_value('InvalidOption', 'SomeValue')
		# Verify it wasn't added to options
		self.assertFalse(cfg.has_value('InvalidOption'))

	def test_spoof_group_load(self):
		"""Test spoof_group functionality when loading config without sections"""
		cfg = INIConfig('GameGroup', os.path.join(here, 'data', 'test_ini_spoof.ini'))
		cfg.spoof_group = True
		cfg.add_option({
			'name': 'StringKey',
			'section': 'GameGroup',
			'key': 'StringKey',
		})
		cfg.add_option({
			'name': 'IntKey',
			'section': 'GameGroup',
			'key': 'IntKey',
			'type': 'int'
		})
		cfg.load()

		# Values should be accessible even though the file has no section headers
		self.assertEqual(cfg.get_value('StringKey'), 'TestValue')
		self.assertEqual(cfg.get_value('IntKey'), 100)

	def test_spoof_group_set_and_save(self):
		"""Test spoof_group when setting values and saving"""
		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test_spoof.ini')
			shutil.copyfile(
				os.path.join(here, 'data', 'test_ini_spoof.ini'),
				path
			)

			cfg = INIConfig('GameGroup', path)
			cfg.spoof_group = True
			cfg.add_option({
				'name': 'StringKey',
				'section': 'GameGroup',
				'key': 'StringKey',
			})
			cfg.add_option({
				'name': 'NewKey',
				'section': 'GameGroup',
				'key': 'NewKey',
			})
			cfg.load()

			# Modify and save
			cfg.set_value('StringKey', 'ModifiedValue')
			cfg.set_value('NewKey', 'NewValue')
			cfg.save()

			# Verify file doesn't have [GameGroup] header
			with open(path, 'r') as f:
				content = f.read()
			self.assertNotIn('[GameGroup]', content)
			self.assertIn('modifiedvalue', content.lower())
			self.assertIn('newkey', content.lower())
			self.assertIn('newvalue', content.lower())

			# Reload and verify
			cfg2 = INIConfig('GameGroup', path)
			cfg2.spoof_group = True
			cfg2.add_option({
				'name': 'StringKey',
				'section': 'GameGroup',
				'key': 'StringKey',
			})
			cfg2.add_option({
				'name': 'NewKey',
				'section': 'GameGroup',
				'key': 'NewKey',
			})
			cfg2.load()
			self.assertEqual(cfg2.get_value('StringKey'), 'ModifiedValue')
			self.assertEqual(cfg2.get_value('NewKey'), 'NewValue')

	def test_multiple_sections(self):
		"""Test working with multiple sections simultaneously"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'TestSectionValue',
			'section': 'TestSection',
			'key': 'StringKey',
		})
		cfg.add_option({
			'name': 'AnotherSectionValue',
			'section': 'AnotherSection',
			'key': 'Setting1',
		})
		cfg.load()

		self.assertEqual(cfg.get_value('TestSectionValue'), 'TestValue')
		self.assertEqual(cfg.get_value('AnotherSectionValue'), 'Value1')
		self.assertTrue(cfg.has_value('TestSectionValue'))
		self.assertTrue(cfg.has_value('AnotherSectionValue'))

	def test_section_none_without_spoof(self):
		"""Test that section=None without spoof_group returns default"""
		cfg = INIConfig('test', os.path.join(here, 'data', 'test_ini_simple.ini'))
		cfg.add_option({
			'name': 'NoneSection',
			'section': None,
			'key': 'TestKey',
			'default': 'DefaultValue'
		})
		cfg.load()

		# Without spoof_group, section=None should not find the value
		value = cfg.get_value('NoneSection')
		self.assertEqual(value, 'DefaultValue')

	def test_section_none_with_spoof(self):
		"""Test that section=None with spoof_group uses the group name"""
		cfg = INIConfig('GameGroup', os.path.join(here, 'data', 'test_ini_spoof.ini'))
		cfg.spoof_group = True
		cfg.add_option({
			'name': 'NoneSection',
			'section': None,
			'key': 'StringKey',
		})
		cfg.load()

		# With spoof_group, section=None should be replaced with group name
		value = cfg.get_value('NoneSection')
		self.assertEqual(value, 'TestValue')


if __name__ == '__main__':
	unittest.main()
