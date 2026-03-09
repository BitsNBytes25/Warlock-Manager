from packaging.version import Version
import re


def parse_version(version_string: str) -> Version:
	"""
	Parse a version string into a Version object.

	Supports standard semantic versioning (e.g., "1.2.3") and pre-release versions
	(e.g., "1.0.0a1", "2.0.0rc1").

	:param version_string: The version string to parse
	:return: A Version object
	:raises ValueError: If the version string is invalid
	"""
	try:
		return Version(version_string)
	except Exception as e:
		raise ValueError(f"Invalid version string: {version_string}") from e


def compare_versions(version1: str | Version, version2: str | Version) -> int:
	"""
	Compare two versions.

	:param version1: First version as string or Version object
	:param version2: Second version as string or Version object
	:return: -1 if version1 < version2, 0 if equal, 1 if version1 > version2
	"""
	v1 = parse_version(version1) if isinstance(version1, str) else version1
	v2 = parse_version(version2) if isinstance(version2, str) else version2

	if v1 < v2:
		return -1
	elif v1 > v2:
		return 1
	else:
		return 0


def is_version_newer(current: str | Version, candidate: str | Version) -> bool:
	"""
	Check if a candidate version is newer than the current version.

	:param current: The current version
	:param candidate: The candidate version to check
	:return: True if candidate is newer than current
	"""
	return compare_versions(candidate, current) < 0


def is_version_older(current: str | Version, candidate: str | Version) -> bool:
	"""
	Check if a candidate version is older than the current version.

	:param current: The current version
	:param candidate: The candidate version to check
	:return: True if candidate is older than current
	"""
	return compare_versions(candidate, current) > 0


def is_version_equal(version1: str | Version, version2: str | Version) -> bool:
	"""
	Check if two versions are equal.

	:param version1: The first version
	:param version2: The second version
	:return: True if versions are equal
	"""
	return compare_versions(version1, version2) == 0


def get_major_version(version: str | Version) -> int:
	"""
	Extract the major version number from a version string.

	:param version: The version string or Version object
	:return: The major version number
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.major


def get_minor_version(version: str | Version) -> int:
	"""
	Extract the minor version number from a version string.

	:param version: The version string or Version object
	:return: The minor version number
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.minor


def get_patch_version(version: str | Version) -> int:
	"""
	Extract the patch version number from a version string.

	:param version: The version string or Version object
	:return: The patch version number
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.micro


def is_prerelease(version: str | Version) -> bool:
	"""
	Check if a version is a pre-release (alpha, beta, rc, etc).

	:param version: The version string or Version object
	:return: True if the version is a pre-release
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.is_prerelease


def is_postrelease(version: str | Version) -> bool:
	"""
	Check if a version is a post-release.

	:param version: The version string or Version object
	:return: True if the version is a post-release
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.is_postrelease


def is_devrelease(version: str | Version) -> bool:
	"""
	Check if a version is a development release.

	:param version: The version string or Version object
	:return: True if the version is a development release
	"""
	v = parse_version(version) if isinstance(version, str) else version
	return v.is_devrelease


def extract_version_from_string(text: str) -> str | None:
	"""
	Extract a version string from arbitrary text using regex pattern matching.

	Matches patterns like "v1.2.3", "1.2.3", "version 1.2.3", etc.

	:param text: The text to search
	:return: The extracted version string, or None if no version is found
	"""
	# Match common version patterns: v1.2.3, 1.2.3, 1.2.3a1, 1.2.3-rc1, etc
	pattern = r'v?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z]+\d+)?(?:[.\-_](?:alpha|beta|rc|a|b|post|dev)\d*)?)'
	match = re.search(pattern, text, re.IGNORECASE)
	return match.group(1) if match else None


def normalize_version(version: str) -> str:
	"""
	Normalize a version string to standard semantic versioning format.

	Converts various formats to a consistent Version object representation.

	:param version: The version string to normalize
	:return: The normalized version string
	"""
	v = parse_version(version)
	return str(v)


def get_version_distance(version1: str | Version, version2: str | Version) -> tuple[int, int, int]:
	"""
	Get the distance between two versions in terms of major, minor, and patch.

	:param version1: The first version
	:param version2: The second version
	:return: A tuple of (major_diff, minor_diff, patch_diff) representing the distance
	"""
	v1 = parse_version(version1) if isinstance(version1, str) else version1
	v2 = parse_version(version2) if isinstance(version2, str) else version2

	major_diff = v2.major - v1.major
	minor_diff = v2.minor - v1.minor
	patch_diff = v2.micro - v1.micro

	return (major_diff, minor_diff, patch_diff)


def is_version_compatible(
	current: str | Version,
	minimum_required: str | Version,
	maximum_required: str | Version | None = None) -> bool:
	"""
	Check if a current version is compatible with required version constraints.

	Supports checking minimum required version and optionally maximum allowed version.

	:param current: The current version
	:param minimum_required: The minimum required version
	:param maximum_required: The maximum allowed version (optional, None for no upper bound)
	:return: True if current version is compatible
	"""
	v_current = parse_version(current) if isinstance(current, str) else current
	v_min = parse_version(minimum_required) if isinstance(minimum_required, str) else minimum_required

	if v_current < v_min:
		return False

	if maximum_required is not None:
		v_max = parse_version(maximum_required) if isinstance(maximum_required, str) else maximum_required
		if v_current > v_max:
			return False

	return True
