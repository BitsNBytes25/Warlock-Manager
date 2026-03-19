from abc import ABC, abstractmethod

from warlock_manager.libs.download import download_file, download_json
from warlock_manager.apps.base_app import BaseApp


class ManualApp(BaseApp, ABC):
	"""
	Application installer for manual installation.

	Generally these are apps which require manual downloads and do not support an app store such as Steam.
	"""

	@abstractmethod
	def get_latest_version(self) -> str | None:
		"""
		Get the latest version available of the app.
		:return:
		"""
		...

	def download_file(self, url: str, destination: str):
		"""
		Download a file from a URL to a destination path.

		:param url: The URL to download from
		:param destination: The local file path to save the downloaded file to
		:return:
		"""
		download_file(self, url, destination)

	def download_json(self, url: str) -> dict:
		"""
		Download JSON data from a URL and return it as a dictionary.

		This method supports caching, so the result is cached to disk,
		and subsequent calls pull from that cache for a time.

		:param url: The URL to download from
		:return: The JSON data as a dictionary
		"""
		return download_json(self, url)
