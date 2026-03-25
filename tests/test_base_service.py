import os
import shutil
import tempfile
import unittest

from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs import utils

here = os.path.dirname(os.path.realpath(__file__))


class TestApp(BaseApp):
	def __init__(self):
		super().__init__()
		self.name = "Test App"
		self.desc = 'Testing application'
		self.service_handler = TestService
		self.services = ['test-service']


class TestService(BaseService):
	def get_executable(self) -> str:
		return '/usr/bin/true'

	def get_port_definitions(self) -> list:
		pass

	def get_game_pid(self) -> int:
		pass


class TestBaseService(unittest.TestCase):
	def test_read_systemd(self):
		app = TestApp()
		svc = TestService('test-service', app)
		svc._service_file = os.path.join(here, 'data', 'sample.service')
		config = svc.get_systemd_config()
		self.assertEqual(2, len(config['Service']['ExecStartPre']), 'Expected exactly 2 parameters for ExecStartPre')
		self.assertIn('/bin/sh -c "foo && bar && baz"', config['Service']['ExecStartPre'])
		self.assertIn('/bin/sh -c "magic"', config['Service']['ExecStartPre'])
		self.assertEqual('/usr/bin/true', config['Service']['ExecStart'])

	def test_write_systemd(self):
		app = TestApp()
		svc = TestService('test-service', app)
		svc._service_file = os.path.join(here, 'data', 'sample.service')

		with tempfile.TemporaryDirectory() as td:
			path = os.path.join(td, 'sample.service')
			shutil.copyfile(svc._service_file, path)
			svc._service_file = path

			svc.build_systemd_config()

			with open(path, 'r') as f:
				data_new = f.read()
			# Most of the parameters in service files are dyanmic based on the environment,
			# but we can at least check for the presence of the expected structure.
			self.assertIn('Description=%s' % app.desc, data_new)
			self.assertIn('Type=simple', data_new)
			self.assertIn('ExecStart=%s' % svc.get_executable(), data_new)
			self.assertIn('WorkingDirectory=%s' % svc.get_app_directory(), data_new)
			self.assertIn('EnvironmentFile=%s/Environments/%s.env' % (utils.get_app_directory(), svc.service), data_new)
