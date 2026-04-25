import os
import subprocess
import json
import time
import pwd

from warlock_manager.libs import cache
from warlock_manager.libs.logger import logger


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

	_memory_cache = {}

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

		self.executable: str | None = self.cmd[0] if len(self.cmd) > 0 else None
		"""
		str: The executable name of the command
		"""

		self.uses: str | None = 'stdout'
		"""
		str: Whether to use stdout or stderr for output ('stdout' or 'stderr')
		Set to None to disable output capture and just check return code.
		This means stdout and stderr will be streamed instead.
		"""

		self.cacheable: int | bool = False
		"""
		Set to a value > 0 if this command can be cached for N amount of seconds.

		Commands that are cacheable are stored on the filesystem to allow for persistent cache between runs
		"""

		self.memory_cacheable: int | bool = False
		"""
		Set to a value > 0 if this command can be cached in memory for N amount of seconds.

		These commands are NOT persistent across calls!
		"""

		self._cwd: str | None = None
		"""
		The current working directory for this command
		"""

	def sudo(self, runas: str | int) -> 'Cmd':
		"""
		Run this command as another user using sudo.

		If runas is a string, it will be treated as a username.
		If runas is an int, it will be treated as a group ID.

		If the requested user is the same as the current script runner, no sudo prefix will be added.

		:param runas:
		:return:
		"""
		if isinstance(runas, str):
			# Get the name of the user owning the current process
			# use pwd instead of os.getlogin to address CI tests on 3.13
			current_user = pwd.getpwuid(os.geteuid()).pw_name
			if current_user == runas:
				# If we're already running as this user, no need to prefix with sudo
				return self
			prefix = ['sudo', '-u', runas]
		else:
			if os.geteuid() == runas:
				# If we're already running as this user, no need to prefix with sudo
				return self
			prefix = ['sudo', '-u', '#%s' % runas]

		self.cmd = prefix + self.cmd
		self.result = None
		return self

	def use_stdout(self) -> 'Cmd':
		"""
		Set this command to use stdout for output instead of stderr.
		:return:
		"""
		self.uses = 'stdout'
		return self

	def use_stderr(self) -> 'Cmd':
		"""
		Set this command to use stderr for output instead of stdout.
		:return:
		"""
		self.uses = 'stderr'
		return self

	def stream_output(self) -> 'Cmd':
		"""
		Set this command to stream to stdout/stderr directly.  Useful for long-running commands.
		:return:
		"""
		self.uses = None
		return self

	def is_cacheable(self, expires: int = 3600) -> 'Cmd':
		"""
		Set this command as cacheable for N seconds.
		:param expires:
		:return:
		"""
		self.cacheable = expires
		return self

	def is_memory_cacheable(self, expires: int = 2) -> 'Cmd':
		"""
		Set this command as cacheable in memory for N seconds.
		:param expires:
		:return:
		"""
		self.memory_cacheable = expires
		return self

	def cwd(self, path: str | None) -> 'Cmd':
		"""
		Set the current working directory for this command.
		:param path:
		:return:
		"""
		self._cwd = path
		return self

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

	def try_cache(self) -> str | None:
		if self.cacheable is True:
			# Convert cacheable to a default number of seconds
			self.cacheable = 60 * 30

		if self.uses is None:
			# Not supported for streaming commands
			return None

		return cache.get_cache(' '.join(self.cmd), expires=self.cacheable)

	def run(self):
		"""
		Run the command and capture the result. Caches the result so subsequent calls don't re-run the command.

		:return:
		"""
		if self.result is None:
			logger.debug('Running command: %s' % ' '.join(self.cmd))
			if self.memory_cacheable is not False:
				key = ' '.join(self.cmd)
				if key in self._memory_cache:
					cached_time, cached, code = Cmd._memory_cache[key]
					if cached_time + self.memory_cacheable >= time.time():
						logger.debug('Using memory cached result instead')
						self.result = CmdFakeResponse(
							cached if self.uses == 'stdout' else '',
							cached if self.uses == 'stderr' else '',
							0
						)
						return self.result

			if self.cacheable is not False:
				cached = self.try_cache()
				if cached is not None:
					logger.debug('Using cached result instead')
					self.result = CmdFakeResponse(
						cached if self.uses == 'stdout' else '',
						cached if self.uses == 'stderr' else '',
						0
					)
					return self.result

			try:
				capture_output = self.uses is not None
				self.result = subprocess.run(
					self.cmd,
					capture_output=capture_output,
					check=False,
					cwd=self._cwd,
					encoding='utf-8'
				)
			except FileNotFoundError as e:
				self.result = CmdFakeResponse('', str(e), 127)
			except OSError as e:
				self.result = CmdFakeResponse('', str(e), 1)
			finally:
				if self.result.stdout:
					logger.debug('STDOUT: %s' % self.result.stdout.strip())
				if self.result.stderr:
					logger.debug('STDERR: %s' % self.result.stderr.strip())
				logger.debug('Return code: %d' % self.result.returncode)

		# Cache all responses to memory if requested, saves time on failed lookup checks.
		if self.memory_cacheable is not False:
			key = ' '.join(self.cmd)
			if self.uses == 'stdout':
				Cmd._memory_cache[key] = (time.time(), self.result.stdout, self.result.returncode)
			elif self.uses == 'stderr':
				Cmd._memory_cache[key] = (time.time(), self.result.stderr, self.result.returncode)
			else:
				logger.warning('Attempting to cache command output without capturing it. This is not supported!')

		if self.result.returncode == 0:
			# Successful executions can be cached to disk
			if self.cacheable is not False:
				# Do we save stdout or stderr?
				if self.uses == 'stdout':
					cache.save_cache(' '.join(self.cmd), self.result.stdout)
				elif self.uses == 'stderr':
					cache.save_cache(' '.join(self.cmd), self.result.stderr)
				else:
					logger.warning('Attempting to cache command output without capturing it. This is not supported!')

		return self.result

	def extend(self, args: list) -> 'Cmd':
		"""
		Extend the command with additional arguments.
		:param args:
		"""
		self.cmd = self.cmd + args
		self.result = None
		return self

	def append(self, arg: str) -> 'Cmd':
		"""
		Append a single argument to the command.
		:param arg:
		"""
		self.cmd.append(arg)
		self.result = None
		return self


class PipeCmd(Cmd):
	"""
	Convenience wrapper for piping command output to a parent process
	"""

	def run(self):
		"""
		Run the command in the background using nohup. Caches the result so subsequent calls don't re-run the command.

		:return:
		"""
		if self.result is None:

			if self.cacheable is not False:
				logger.warning('Piped commands cannot be cached!')

			try:
				logger.debug('Running piped command: %s' % ' '.join(self.cmd))
				self.result = subprocess.Popen(
					self.cmd,
					cwd=self._cwd,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE
				)
			except FileNotFoundError as e:
				self.result = CmdFakeResponse('', str(e), 127)
			except OSError as e:
				self.result = CmdFakeResponse('', str(e), 1)

		return self.result


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

			if self.cacheable is not False:
				logger.warning('Background commands cannot be cached!')

			try:
				logger.debug('Running background command: %s' % ' '.join(self.cmd))
				self.result = subprocess.Popen(
					self.cmd,
					cwd=self._cwd,
					stdout=subprocess.DEVNULL,
					stderr=subprocess.DEVNULL
				)
			except FileNotFoundError as e:
				self.result = CmdFakeResponse('', str(e), 127)
			except OSError as e:
				self.result = CmdFakeResponse('', str(e), 1)

		return self.result
