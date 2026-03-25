import os
import unittest
from unittest.mock import patch, MagicMock

from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.socket_service import SocketService

here = os.path.dirname(os.path.realpath(__file__))


class TestApp(BaseApp):
	def __init__(self):
		super().__init__()
		self.name = "Test App"
		self.desc = 'Testing application'
		self.services = ['test-socket-service']


class TestSocketService(SocketService):
	def get_executable(self) -> str:
		return '/usr/bin/true'

	def get_port_definitions(self) -> list:
		pass

	def get_game_pid(self) -> int:
		pass

	def is_stopped(self) -> bool:
		return False


class TestSocketServiceWatch(unittest.TestCase):

	def test_watch_callback_returns_true(self):
		"""Test that watch returns True when callback signals completion"""
		app = TestApp()
		svc = TestSocketService('test-socket-service', app)

		# Mock the subprocess.Popen to simulate journal output
		mock_process = MagicMock()
		mock_process.stdout.readline.side_effect = [
			'Line 1\n',
			'Line 2 - PLAYERS: 5\n',  # This line will trigger the callback
			'Line 3\n'
		]

		# Patch select.select to always indicate output is ready for each readline call
		with patch('subprocess.Popen', return_value=mock_process):
			def callback(line):
				return 'PLAYERS' in line

			result = svc.watch(callback, timeout=10)

			self.assertTrue(result, "watch should return True when callback signals completion")

	def test_watch_timeout(self):
		"""Test that watch returns False on timeout"""
		app = TestApp()
		svc = TestSocketService('test-socket-service', app)

		# Mock the subprocess.Popen to simulate journal output that never matches
		mock_process = MagicMock()
		mock_process.stdout.readline.side_effect = [
													   'Line 1\n',
													   'Line 2\n',
													   'Line 3\n'
												   ] * 100  # Endless stream

		# Patch select.select to always indicate output is ready for each readline call
		select_side_effect = [([mock_process.stdout], [], [])] * 22

		with patch('subprocess.Popen', return_value=mock_process):
			with patch('select.select', side_effect=select_side_effect):
				with patch(
					'time.time',
					side_effect=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5]
				):
					def callback(line):
						pass

					result = svc.watch(callback, timeout=2)

					self.assertFalse(result, "watch should return False on timeout")

	def test_watch_callback_exception(self):
		"""Test that watch handles exceptions from callback gracefully"""
		app = TestApp()
		svc = TestSocketService('test-socket-service', app)

		# Mock the subprocess.Popen
		mock_process = MagicMock()
		mock_process.stdout.readline.side_effect = [
			'Line 1\n',
		]

		# Patch select.select to indicate output is ready for the readline call
		with patch('subprocess.Popen', return_value=mock_process):
			with patch('select.select', side_effect=[([mock_process.stdout], [], [])]):
				def callback(line):
					raise ValueError("Test exception")

				# The callback exception is caught and logged, resulting in False return
				result = svc.watch(callback, timeout=10)
				self.assertFalse(result, "watch should return False when callback raises exception")


if __name__ == '__main__':
	unittest.main()
