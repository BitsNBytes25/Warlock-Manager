import unittest
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService


class TestApp(BaseApp):
	def __init__(self):
		super().__init__()
		self.name = "Test App"
		self.desc = 'Testing application'
		self.service_handler = TestService
		self.services = ['test-service']


class TestService(BaseService):
	def get_port_definitions(self) -> list:
		return [(8080, 'tcp', 'Test Port')]

	def get_game_pid(self) -> int:
		123

	def __init__(self, service: str, game: TestApp):
		super().__init__(service, game)
		self.load()


class TestApplication(unittest.TestCase):
	def test_app(self):
		app = TestApp()
		self.assertEqual('Test App', app.name)
		self.assertEqual('Testing application', app.desc)
		self.assertEqual(1, len(app.get_services()))

		svc = app.get_services()[0]
		self.assertEqual('test-service', svc.service)
		self.assertEqual('test-service', app.get_service('test-service').get_name())
