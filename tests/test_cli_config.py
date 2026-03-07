import os
import shutil
import tempfile
import unittest

from warlock_manager.config.cli_config import CLIConfig

here = os.path.dirname(os.path.realpath(__file__))


class TestCLIConfig(unittest.TestCase):
	def test_ark(self):
		cfg = CLIConfig('test', os.path.join(here, 'data', 'cli_ark.service'))
		cfg.format = 'ExecStart=/path/to/proton run ArkAscendedServer.exe Ark?listen[OPTIONS]'
		cfg.add_option({
			'name': 'Session Name',
			'section': 'option',
			'key': 'SessionName',
		})
		cfg.add_option({
			'name': 'RCON Port',
			'section': 'option',
			'key': 'RCONPort',
			'default': 0,
			'type': 'int'
		})
		cfg.add_option({
			'name': 'RCON Enabled',
			'section': 'option',
			'key': 'RCONEnabled',
			'default': False,
			'type': 'bool'
		})
		cfg.add_option({
			'name': 'Flag1',
			'section': 'flag',
			'key': 'Flag1',
			'default': '',
			'type': 'str'
		})
		cfg.add_option({
			'name': 'Flag2',
			'section': 'flag',
			'key': 'Flag2',
			'default': '',
			'type': 'str'
		})
		cfg.load()

		# SessionName="My Ark Server"?RCONPort=32330 -Flag1=Value1 -Flag2="Some value 2"

		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.service')
			shutil.copyfile(cfg.path, path)
			orig_path = cfg.path
			cfg.path = path

			cfg.save()

			with open(path, 'r') as f:
				data_new = f.read()
			with open(orig_path, 'r') as f:
				data_orig = f.read()
			self.assertEqual(data_orig, data_new)

		self.assertTrue(cfg.get_value('RCON Enabled'))
		self.assertEqual(
			'?SessionName="My Ark Server"?RCONPort=32330?RCONEnabled=True -Flag1=Value1 -Flag2="Some value 2"',
			str(cfg)
		)
		cfg.set_value('RCON Enabled', False)
		self.assertFalse(cfg.get_value('RCON Enabled'))
		self.assertEqual(
			'?SessionName="My Ark Server"?RCONPort=32330?RCONEnabled=False -Flag1=Value1 -Flag2="Some value 2"',
			str(cfg)
		)

	def test_similar_arguments(self):
		cfg = CLIConfig('test')
		cfg.add_option({
			'name': 'Modifier - Player Events',
			'section': 'flag',
			'key': 'setkey playerevents',
			'default': False,
			'type': 'bool'
		})
		cfg.add_option({
			'name': 'Modifier - Passive Mobs',
			'section': 'flag',
			'key': 'setkey passivemobs',
			'default': False,
			'type': 'bool'
		})
		cfg.add_option({
			'name': 'Modifier - No Map',
			'section': 'flag',
			'key': 'setkey nomap',
			'default': False,
			'type': 'bool'
		})
		cfg.load('-setkey passivemobs')

		self.assertFalse(cfg.get_value('Modifier - Player Events'))
		self.assertTrue(cfg.get_value('Modifier - Passive Mobs'))
		self.assertFalse(cfg.get_value('Modifier - No Map'))

		cfg.set_value('Modifier - Player Events', True)
		cfg.set_value('Modifier - No Map', True)

		self.assertTrue(cfg.get_value('Modifier - Player Events'))
		self.assertTrue(cfg.get_value('Modifier - Passive Mobs'))
		self.assertTrue(cfg.get_value('Modifier - No Map'))

		self.assertEqual('-setkey playerevents -setkey passivemobs -setkey nomap', str(cfg))

	def test_valheim(self):
		cfg = CLIConfig('test', os.path.join(here, 'data', 'cli_valheim.service'))
		cfg.format = 'ExecStart=/home/steam/Valheim/AppFiles/valheim_server.x86_64 [OPTIONS]'
		cfg.flag_sep = ' '
		cfg.add_option({
			'name': 'Name',
			'section': 'flag',
			'key': 'name',
			'default': '',
			'type': 'str'
		})
		cfg.add_option({
			'name': 'Port',
			'section': 'flag',
			'key': 'port',
			'default': 0,
			'type': 'int'
		})
		cfg.add_option({
			'name': 'World',
			'section': 'flag',
			'key': 'world',
			'default': '',
			'type': 'str'
		})
		cfg.add_option({
			'name': 'Password',
			'section': 'flag',
			'key': 'password',
			'default': '',
			'type': 'str'
		})
		cfg.add_option({
			'name': 'Crossplay',
			'section': 'flag',
			'key': 'crossplay',
			'default': False,
			'type': 'bool'
		})
		cfg.add_option({
			'name': 'Modifier Raids',
			'section': 'flag',
			'key': 'modifier raids',
			'default': 'none',
			'type': 'str'
		})
		cfg.load()

		self.assertEqual('My server', cfg.get_value('Name'))
		self.assertEqual(2456, cfg.get_value('Port'))
		self.assertEqual('Dedicated', cfg.get_value('World'))
		self.assertEqual('secret', cfg.get_value('Password'))
		self.assertEqual(True, cfg.get_value('Crossplay'))
		self.assertEqual('none', cfg.get_value('Modifier Raids'))

		self.assertEqual(
			'-name "My server" -port 2456 -world Dedicated -password secret -crossplay -modifier raids none',
			str(cfg)
		)

		cfg.set_value('Crossplay', False)
		self.assertEqual(False, cfg.get_value('Crossplay'))
		self.assertEqual(
			'-name "My server" -port 2456 -world Dedicated -password secret -modifier raids none',
			str(cfg)
		)

		cfg.set_value('Crossplay', True)
		self.assertEqual(True, cfg.get_value('Crossplay'))

		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'test.service')
			shutil.copyfile(cfg.path, path)
			orig_path = cfg.path
			cfg.path = path

			cfg.save()

			with open(path, 'r') as f:
				data_new = f.read()
			with open(orig_path, 'r') as f:
				data_orig = f.read()
			self.assertEqual(data_orig, data_new)
