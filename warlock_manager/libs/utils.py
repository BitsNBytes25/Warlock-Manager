import logging
import os
import pwd
import sys
from typing_extensions import deprecated


@deprecated('Please use utils.get_base_directory instead to avoid confusion')
def get_app_directory() -> str:
	"""
	Get the base directory for this game installation.

	This directory usually will contain manage.py, AppFiles, Backups, and other related files.

	:return:
	"""
	return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_base_directory() -> str:
	"""
	Get the base directory for this game installation.

	This directory usually will contain manage.py, AppFiles, Backups, and other related files.

	:return:
	"""
	return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_home_directory() -> str:
	"""
	Get the home directory of the user running this application

	:return:
	"""
	return pwd.getpwuid(get_app_uid()).pw_dir


def get_app_uid() -> int:
	"""
	Get the user ID that should own the game files, based on the ownership of the executable directory
	:return:
	"""

	# Pull the user id and group id based off the ownership of 'AppFiles' in the executable directory
	# If the directory does not exist, (normal for new installations), keep going up until we find one
	check_dir = get_app_directory()
	while not os.path.exists(check_dir):
		check_dir = os.path.dirname(check_dir)
		if check_dir == '/' or check_dir == '':
			# Reached the root directory without finding an existing directory, default to current user and group
			return os.geteuid()
	else:
		stat_info = os.stat(check_dir)
		return stat_info.st_uid


def get_app_gid() -> int:
	"""
	Get the group ID that should own the game files, based on the ownership of the executable directory
	:return:
	"""

	# Pull the user id and group id based off the ownership of 'AppFiles' in the executable directory
	# If the directory does not exist, (normal for new installations), keep going up until we find one
	check_dir = get_app_directory()
	while not os.path.exists(check_dir):
		check_dir = os.path.dirname(check_dir)
		if check_dir == '/' or check_dir == '':
			# Reached the root directory without finding an existing directory, default to current user and group
			return os.getegid()
	else:
		stat_info = os.stat(check_dir)
		return stat_info.st_gid


def ensure_file_ownership(file: str):
	"""
	Try to set the ownership of the given file to match the ownership of the game installation directory.
	:param file:
	:return:
	"""
	if os.geteuid() == 0:
		# If running as root, chown the environment file to the game user
		uid = get_app_uid()
		gid = get_app_gid()

		logging.debug('Ensuring ownership of %s to %s:%s' % (file, uid, gid))
		os.chown(file, uid, gid)
		if os.path.isdir(file):
			for root, dirs, files in os.walk(file):
				for momo in dirs:
					os.chown(os.path.join(root, momo), uid, gid)
				for momo in files:
					os.chown(os.path.join(root, momo), uid, gid)


def ensure_file_parent_exists(file: str):
	"""
	A replacement of os.makedirs, but also sets permissions as it creates the directories.

	This variation expects a child file to be requested.
	It will create the parent directory if it does not exist, but will not touch the actual file itself.

	:param file:
	:return:
	"""
	return makedirs(os.path.dirname(file))


def makedirs(target_dir: str):
	"""
	A replacement of os.makedirs, but also sets permissions as it creates the directories.

	:param target_dir:
	:return:
	"""
	if os.path.exists(target_dir):
		# Parent directory exists, nothing to do
		return

	# Ensure the directory exists within the context of either this game or the game owner's home directory
	if not (target_dir.startswith(get_app_directory()) or target_dir.startswith(get_home_directory())):
		raise Exception('Cannot create directory outside of game directory: %s' % target_dir)

	# Iterate up until the parent directory exists.
	# This will determine where we need to send file_ownership to.
	# This is done so we don't have to chown the entire game directory.
	test_dir = target_dir
	# Last child will be the last directory that did not exist; we'll issue the chown there.
	last_child = target_dir
	while test_dir != '/' and test_dir != '':
		test_dir = os.path.dirname(test_dir)
		if not os.path.exists(test_dir):
			last_child = test_dir
		else:
			break

	os.makedirs(target_dir, exist_ok=True)
	ensure_file_ownership(last_child)
