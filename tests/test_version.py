import unittest
from warlock_manager.libs.version import (
	parse_version,
	compare_versions,
	is_version_newer,
	is_version_older,
	is_version_equal,
	get_major_version,
	get_minor_version,
	get_patch_version,
	is_prerelease,
	is_postrelease,
	is_devrelease,
	extract_version_from_string,
	normalize_version,
	get_version_distance,
	is_version_compatible,
)
from packaging.version import Version


class TestVersionParsing(unittest.TestCase):
	"""Test version parsing functionality"""

	def test_parse_valid_version(self):
		v = parse_version("1.2.3")
		self.assertIsInstance(v, Version)
		self.assertEqual(v.major, 1)
		self.assertEqual(v.minor, 2)
		self.assertEqual(v.micro, 3)

	def test_parse_version_with_prerelease(self):
		v = parse_version("1.0.0a1")
		self.assertTrue(v.is_prerelease)

	def test_parse_version_with_postrelease(self):
		v = parse_version("1.0.0.post1")
		self.assertTrue(v.is_postrelease)

	def test_parse_version_with_devrelease(self):
		v = parse_version("1.0.0.dev0")
		self.assertTrue(v.is_devrelease)

	def test_parse_invalid_version(self):
		with self.assertRaises(ValueError):
			parse_version("not.a.version")


class TestVersionComparison(unittest.TestCase):
	"""Test version comparison functionality"""

	def test_compare_versions_less_than(self):
		result = compare_versions("1.0.0", "2.0.0")
		self.assertEqual(result, -1)

	def test_compare_versions_greater_than(self):
		result = compare_versions("2.0.0", "1.0.0")
		self.assertEqual(result, 1)

	def test_compare_versions_equal(self):
		result = compare_versions("1.0.0", "1.0.0")
		self.assertEqual(result, 0)

	def test_compare_with_version_objects(self):
		v1 = parse_version("1.0.0")
		v2 = parse_version("2.0.0")
		result = compare_versions(v1, v2)
		self.assertEqual(result, -1)


class TestVersionBooleanComparisons(unittest.TestCase):
	"""Test boolean version comparison helpers"""

	def test_is_version_newer(self):
		self.assertTrue(is_version_newer("1.0.0", "2.0.0"))
		self.assertFalse(is_version_newer("2.0.0", "1.0.0"))
		self.assertFalse(is_version_newer("1.0.0", "1.0.0"))

	def test_is_version_older(self):
		self.assertTrue(is_version_older("2.0.0", "1.0.0"))
		self.assertFalse(is_version_older("1.0.0", "2.0.0"))
		self.assertFalse(is_version_older("1.0.0", "1.0.0"))

	def test_is_version_equal(self):
		self.assertTrue(is_version_equal("1.0.0", "1.0.0"))
		self.assertFalse(is_version_equal("1.0.0", "1.0.1"))


class TestVersionComponentExtraction(unittest.TestCase):
	"""Test extracting version components"""

	def test_get_major_version(self):
		self.assertEqual(get_major_version("3.2.1"), 3)
		self.assertEqual(get_major_version(parse_version("10.5.0")), 10)

	def test_get_minor_version(self):
		self.assertEqual(get_minor_version("3.2.1"), 2)
		self.assertEqual(get_minor_version(parse_version("1.7.0")), 7)

	def test_get_patch_version(self):
		self.assertEqual(get_patch_version("3.2.1"), 1)
		self.assertEqual(get_patch_version(parse_version("1.0.5")), 5)


class TestVersionReleaseType(unittest.TestCase):
	"""Test checking version release types"""

	def test_is_prerelease(self):
		self.assertTrue(is_prerelease("1.0.0a1"))
		self.assertTrue(is_prerelease("1.0.0b2"))
		self.assertTrue(is_prerelease("1.0.0rc3"))
		self.assertFalse(is_prerelease("1.0.0"))

	def test_is_postrelease(self):
		self.assertTrue(is_postrelease("1.0.0.post1"))
		self.assertFalse(is_postrelease("1.0.0"))

	def test_is_devrelease(self):
		self.assertTrue(is_devrelease("1.0.0.dev0"))
		self.assertFalse(is_devrelease("1.0.0"))


class TestVersionExtraction(unittest.TestCase):
	"""Test extracting versions from text"""

	def test_extract_simple_version(self):
		result = extract_version_from_string("Version 1.2.3 released")
		self.assertIsNotNone(result)
		self.assertIn("1.2.3", result)

	def test_extract_version_with_v_prefix(self):
		result = extract_version_from_string("Release v2.0.0 now")
		self.assertIsNotNone(result)
		self.assertIn("2.0.0", result)

	def test_extract_version_with_prerelease(self):
		result = extract_version_from_string("Beta version 1.0.0a1 available")
		self.assertIsNotNone(result)

	def test_extract_no_version(self):
		result = extract_version_from_string("No version here")
		self.assertIsNone(result)


class TestVersionNormalization(unittest.TestCase):
	"""Test version normalization"""

	def test_normalize_simple_version(self):
		result = normalize_version("1.2.3")
		self.assertEqual(result, "1.2.3")

	def test_normalize_version_with_prerelease(self):
		result = normalize_version("1.0.0a1")
		self.assertIn("a1", result)


class TestVersionDistance(unittest.TestCase):
	"""Test calculating distance between versions"""

	def test_version_distance_same(self):
		distance = get_version_distance("1.0.0", "1.0.0")
		self.assertEqual(distance, (0, 0, 0))

	def test_version_distance_major_bump(self):
		distance = get_version_distance("1.0.0", "2.0.0")
		self.assertEqual(distance, (1, 0, 0))

	def test_version_distance_minor_bump(self):
		distance = get_version_distance("1.0.0", "1.2.0")
		self.assertEqual(distance, (0, 2, 0))

	def test_version_distance_patch_bump(self):
		distance = get_version_distance("1.0.0", "1.0.5")
		self.assertEqual(distance, (0, 0, 5))

	def test_version_distance_combined(self):
		distance = get_version_distance("1.2.3", "2.5.8")
		self.assertEqual(distance, (1, 3, 5))


class TestVersionCompatibility(unittest.TestCase):
	"""Test version compatibility checking"""

	def test_compatible_with_minimum(self):
		self.assertTrue(is_version_compatible("2.0.0", "1.0.0"))
		self.assertTrue(is_version_compatible("1.0.0", "1.0.0"))
		self.assertFalse(is_version_compatible("0.9.0", "1.0.0"))

	def test_compatible_with_range(self):
		self.assertTrue(is_version_compatible("1.5.0", "1.0.0", "2.0.0"))
		self.assertFalse(is_version_compatible("2.1.0", "1.0.0", "2.0.0"))
		self.assertFalse(is_version_compatible("0.9.0", "1.0.0", "2.0.0"))

	def test_compatible_with_version_objects(self):
		current = parse_version("1.5.0")
		minimum = parse_version("1.0.0")
		maximum = parse_version("2.0.0")
		self.assertTrue(is_version_compatible(current, minimum, maximum))


if __name__ == '__main__':
	unittest.main()
