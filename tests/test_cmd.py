import unittest
from warlock_manager.libs.cmd import Cmd


class TestCmd(unittest.TestCase):
	def test_exists_true(self):
		cmd = Cmd(["echo"])
		self.assertTrue(cmd.exists)

	def test_exists_false(self):
		cmd = Cmd(["nonexistentbinary12345"])
		self.assertFalse(cmd.exists)
		self.assertFalse(cmd.success)

	def test_text(self):
		cmd = Cmd(["echo", "hello world"])
		self.assertEqual(cmd.text, "hello world")

	def test_lines(self):
		cmd = Cmd(["echo", "line1\nline2"])
		self.assertEqual(cmd.lines, ["line1", "line2"])

	def test_json(self):
		cmd = Cmd(["echo", '{"a": 1, "b": 2}'])
		self.assertEqual(cmd.json, {"a": 1, "b": 2})

	def test_success(self):
		cmd = Cmd(["echo", "ok"])
		self.assertTrue(cmd.success)

	def test_exit_status(self):
		cmd = Cmd(["echo", "ok"])
		self.assertEqual(cmd.exit_status, 0)

	def test_failure(self):
		cmd = Cmd(["false"])
		self.assertFalse(cmd.success)
		self.assertNotEqual(cmd.exit_status, 0)

	def test_json_invalid(self):
		cmd = Cmd(["echo", "notjson"])
		with self.assertRaises(Exception):
			_ = cmd.json


if __name__ == "__main__":
	unittest.main()
