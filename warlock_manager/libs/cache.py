import hashlib
import os
import time

from warlock_manager.libs import utils


def get_cache(some_string: str, expires: int = 3600) -> str | None:
	# Check cache prior to running the command.
	cmd_hash = hashlib.sha256(some_string.encode()).hexdigest()
	cache_path = os.path.join(utils.get_app_directory(), '.cache', cmd_hash)
	if os.path.exists(cache_path) and os.path.getmtime(cache_path) > time.time() - expires:
		with open(cache_path, "r") as f:
			return f.read()
	else:
		return None


def save_cache(some_string: str, content: str):
	cache_path = os.path.join(utils.get_app_directory(), '.cache')
	if not os.path.exists(cache_path):
		os.makedirs(cache_path)
		utils.ensure_file_ownership(cache_path)

	cmd_hash = hashlib.sha256(some_string.encode()).hexdigest()
	cache_path = os.path.join(utils.get_app_directory(), '.cache', cmd_hash)
	with open(cache_path, "w") as f:
		f.write(content)
	utils.ensure_file_ownership(cache_path)
