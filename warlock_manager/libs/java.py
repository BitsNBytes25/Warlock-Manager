import logging

from warlock_manager.libs.version import extract_version_from_string, parse_version
from warlock_manager.libs.cmd import Cmd


def get_java_paths() -> list[str]:
	"""
	Get a list of all Java executable paths available on the system using alternatives.

	:return: A list of paths to Java executables
	"""

	# Try update-alternatives first (Debian-based distros)
	cmd = Cmd(['update-alternatives', '--list', 'java'])
	if cmd.success:
		return cmd.lines

	# Fall back to alternatives (RHEL-based distros)
	cmd = Cmd(['alternatives', '--list', 'java'])
	if cmd.success:
		return [line.split()[2] for line in cmd.lines]

	return []


def find_java_version(version: int) -> str:
	"""
	Find the path to the Java executable for the given version.

	Uses alternatives / update-alternatives to detect paths.

	:param version: The major Java version to find (e.g., 11, 17, 21)
	:return: The path to the Java executable matching the requested version
	:raises RuntimeError: If no Java executable matching the version is found
	"""
	java_paths = get_java_paths()
	java_path = _check_java_versions(java_paths, version)
	if java_path:
		return java_path

	raise OSError(f'No Java {version} installation found using alternatives or update-alternatives')


def _check_java_versions(java_paths: list[str], target_version: int) -> str | None:
	"""
	Check a list of Java paths and return the one matching the target version.

	:param java_paths: List of paths to Java executables
	:param target_version: The major Java version to find
	:return: The path to the matching Java executable, or None if not found
	"""
	logging.debug('Searching for Java version %d' % target_version)
	for java_path in java_paths:
		result = Cmd([java_path, '-version'])
		# Java version information is typically printed to stderr, so we need to use that instead of stdout.
		result.use_stderr()

		if result.success and len(result.lines) > 0:
			# Parse the version output
			version_str = result.lines[0]
			# Use the version library to parse this version string.
			version_str = extract_version_from_string(version_str)
			version = parse_version(version_str)
			logging.debug('%s => %s' % (java_path, version))
			if version.major == 1:
				# For Java 8 and earlier, the version string starts with "1.", so we need to check the minor version
				if version.minor == target_version:
					return java_path
			elif version.major == target_version:
				return java_path

	return None
