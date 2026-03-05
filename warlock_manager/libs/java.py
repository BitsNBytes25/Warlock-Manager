import subprocess
import re


def get_java_paths() -> list[str]:
	"""
	Get a list of all Java executable paths available on the system using alternatives.

	:return: A list of paths to Java executables
	"""
	java_paths = []

	# Try update-alternatives first (Debian-based distros)
	try:
		result = subprocess.run(
			['update-alternatives', '--list', 'java'],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)
		if result.returncode == 0:
			java_paths.extend(result.stdout.strip().split('\n'))
	except FileNotFoundError:
		pass

	# Fall back to alternatives (RHEL-based distros)
	try:
		result = subprocess.run(
			['alternatives', '--list', 'java'],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True
		)
		if result.returncode == 0:
			java_paths.extend([line.split()[1] for line in result.stdout.strip().split('\n') if line.strip()])
	except FileNotFoundError:
		pass

	return java_paths


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
	for java_path in java_paths:
		try:
			result = subprocess.run(
				[java_path, '--version'],
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT,
				text=True,
				timeout=5
			)

			# Parse the version output
			# Java version output looks like "openjdk 11.0.x" or "java 17.0.x"
			version_match = re.search(r'(\d+)\.(\d+)', result.stdout)
			if version_match:
				major_version = int(version_match.group(1))
				if major_version == target_version:
					return java_path
		except (subprocess.TimeoutExpired, OSError, ValueError):
			# Skip this path if we can't execute it or parse the version
			continue

	return None
