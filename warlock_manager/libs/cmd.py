import os
import subprocess
import json
import logging


class CmdFakeResponse:
	"""
	Fake response object to mimic subprocess.CompletedProcess for error handling when the command is not found.
	"""
	def __init__(self, stdout: str, stderr: str, returncode: int):
		self.stdout = stdout
		self.stderr = stderr
		self.returncode = returncode


class Cmd:
	"""
	Simple subprocess wrapper to provide convenience methods for common interactions.
	"""

	def __init__(self, cmd: list):
		"""
		Initialize a new command wrapper with the given command list.
		:param cmd:
		"""
		self.cmd: list = cmd
		"""
		list: The command to run
		"""

		self.result = None
		"""
		CompletedProcess: The result of the command execution
		"""

		self.executable: str | None = cmd[0] if len(cmd) > 0 else None
		"""
		str: The executable name of the command
		"""

		self.uses: str | None = 'stdout'
		"""
		str: Whether to use stdout or stderr for output ('stdout' or 'stderr')
		Set to None to disable output capture and just check return code.
		This means stdout and stderr will be streamed instead.
		"""

	def sudo(self, runas: str | int):
		"""
		Run this command as another user using sudo.

		If runas is a string, it will be treated as a username.
		If runas is an int, it will be treated as a group ID.

		If the requested user is the same as the current script runner, no sudo prefix will be added.

		:param runas:
		:return:
		"""
		if isinstance(runas, str):
			if os.getlogin() == runas:
				# If we're already running as this user, no need to prefix with sudo
				return
			prefix = ['sudo', '-u', runas]
		else:
			if os.geteuid() == runas:
				# If we're already running as this user, no need to prefix with sudo
				return
			prefix = ['sudo', '-u', '#%s' % runas]

		self.cmd = prefix + self.cmd
		self.result = None

	def use_stdout(self):
		"""
		Set this command to use stdout for output instead of stderr.
		:return:
		"""
		self.uses = 'stdout'

	def use_stderr(self):
		"""
		Set this command to use stderr for output instead of stdout.
		:return:
		"""
		self.uses = 'stderr'

	def stream_output(self):
		"""
		Set this command to stream to stdout/stderr directly.  Useful for long-running commands.
		:return:
		"""
		self.uses = None

	@property
	def exists(self) -> bool:
		"""
		Check if this binary exists
		:return:
		"""
		return subprocess.run(['which', self.executable], check=False, stdout=subprocess.PIPE).returncode == 0

	@property
	def text(self) -> str:
		"""
		Get the output of the command as raw text
		:return:
		"""
		if self.uses == 'stdout':
			return self.run().stdout.strip()
		elif self.uses == 'stderr':
			return self.run().stderr.strip()
		else:
			return ''

	@property
	def lines(self) -> list:
		"""
		Get the output of the command as lines of text (as a list)
		:return:
		"""
		return self.text.split('\n')

	@property
	def json(self):
		"""
		Get the output of the command decoded as JSON
		:return:
		"""
		return json.loads(self.text)

	@property
	def success(self) -> bool:
		"""
		Check if the command executed successfully (return code 0)
		:return:
		"""
		return self.run().returncode == 0

	@property
	def exit_status(self) -> int:
		"""
		Get the return code of the command execution
		:return:
		"""
		return self.run().returncode

	def run(self):
		"""
		Run the command and capture the result. Caches the result so subsequent calls don't re-run the command.

		:return:
		"""
		if self.result is None:
			try:
				capture_output = self.uses is not None
				logging.debug('Running command: %s' % ' '.join(self.cmd))
				self.result = subprocess.run(
					self.cmd,
					capture_output=capture_output,
					check=False,
					encoding='utf-8'
				)
			except FileNotFoundError as e:
				self.result = CmdFakeResponse('', str(e), 127)
			except OSError as e:
				self.result = CmdFakeResponse('', str(e), 1)
			finally:
				if self.result.stdout:
					logging.debug('STDOUT: %s' % self.result.stdout.strip())
				if self.result.stderr:
					logging.debug('STDERR: %s' % self.result.stderr.strip())
				logging.debug('Return code: %d' % self.result.returncode)

		return self.result

	def extend(self, args: list):
		"""
		Extend the command with additional arguments.
		:param args:
		"""
		self.cmd = self.cmd + args
		self.result = None

	def append(self, arg: str):
		"""
		Append a single argument to the command.
		:param arg:
		"""
		self.cmd.append(arg)
		self.result = None


class BackgroundCmd(Cmd):
	"""
	Convenience wrapper for running commands in the background (with nohup).
	"""

	def run(self):
		"""
		Run the command in the background using nohup. Caches the result so subsequent calls don't re-run the command.

		:return:
		"""
		if self.result is None:
			try:
				self.result = subprocess.Popen(
					self.cmd,
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL,
					preexec_fn=lambda: logging.debug('Running background command: %s' % ' '.join(self.cmd))
				)
			except FileNotFoundError as e:
				self.result = CmdFakeResponse('', str(e), 127)
			except OSError as e:
				self.result = CmdFakeResponse('', str(e), 1)

		return self.result
