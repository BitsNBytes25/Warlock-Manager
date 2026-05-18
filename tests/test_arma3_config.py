import os
import unittest

from warlock_manager.config.arma_server_config import ArmaServerConfig

here = os.path.dirname(os.path.realpath(__file__))


class TestArma3Config(unittest.TestCase):
	"""Test cases for ArmaServerConfig class"""

	def test_init(self):
		""" Test basic initialization and loading"""
		cfg = ArmaServerConfig('test', os.path.join(here, 'data', 'arma3.cfg'))
		cfg.load()

	def test_fetch(self):
		cfg = ArmaServerConfig('test', os.path.join(here, 'data', 'arma3.cfg'))
		cfg.load()
		fetched = cfg.fetch()
		self.assertIsInstance(fetched, str)
		# Load the base file to validate against
		with open(cfg.path, 'r') as f:
			expected = f.read()
		self.assertEqual(expected, fetched)

	def test_updates(self):
		cfg = ArmaServerConfig('test', os.path.join(here, 'data', 'arma3.cfg'))
		cfg.add_option({
			'name': 'Hostname',
			'key': 'hostname',
		})
		cfg.add_option({
			'name': 'Some New Key',
			'key': 'some_new_key',
		})
		cfg.add_option({
			'name': 'Some Number',
			'key': 'some_num_key',
			'val_type': 'int'
		})
		cfg.load()

		self.assertEqual('Fun and Test Server', cfg.get_value('Hostname'))
		self.assertTrue(cfg.has_value('Hostname'))
		cfg.set_value('Hostname', 'New Server Name')
		self.assertEqual('New Server Name', cfg.get_value('Hostname'))

		self.assertFalse(cfg.has_value('Some New Key'))
		cfg.set_value('Some New Key', 'New Value')
		self.assertEqual('New Value', cfg.get_value('Some New Key'))
		self.assertTrue(cfg.has_value('Some New Key'))
		self.assertIn('some_new_key = "New Value";', cfg.fetch())

		self.assertFalse(cfg.has_value('Some Number'))
		cfg.set_value('Some Number', 123)
		self.assertEqual(123, cfg.get_value('Some Number'))
		self.assertTrue(cfg.has_value('Some Number'))
		self.assertIn('some_num_key = 123;', cfg.fetch())


if __name__ == '__main__':
	unittest.main()
