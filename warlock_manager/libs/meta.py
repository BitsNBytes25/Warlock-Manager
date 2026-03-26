import json
import os
import sys
from importlib.metadata import version, PackageNotFoundError


def get_meta() -> dict:
	"""
	Get the meta information for this application

	This relates to the information of the _management script_, not of the game.
	:return:
	"""
	meta = {
		'version': 'unknown',
		'url': None,
		'source': None,
		'repo': None,
		'branch': None,
		'commit': None
	}

	try:
		meta['version'] = version("warlock_manager")
	except PackageNotFoundError:
		pass

	version_file = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), '.manage.json')
	if os.path.exists(version_file):
		try:
			with open(version_file, 'r') as f:
				version_data = json.load(f)
				meta['branch'] = version_data['branch']
				meta['commit'] = version_data['commit']
				meta['source'] = version_data['source']
				meta['repo'] = version_data['repo']
		except Exception:
			pass

	if meta['source'] == 'github' and meta['repo'] is not None:
		meta['url'] = 'https://github.com/' + meta["repo"]

	return meta
