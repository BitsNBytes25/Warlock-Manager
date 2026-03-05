from abc import ABC, abstractmethod
import requests

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
		response = requests.get(url, stream=True)
		response.raise_for_status()  # Check if the request was successful

		with open(destination, 'wb') as f:
			for chunk in response.iter_content(chunk_size=8192):
				f.write(chunk)

		# Once complete, set ownership for the downloaded file
		self.ensure_file_ownership(destination)

	def download_json(self, url: str) -> dict:
		"""
		Download JSON data from a URL and return it as a dictionary.

		:param url: The URL to download from
		:return: The JSON data as a dictionary
		"""
		response = requests.get(url)
		response.raise_for_status()  # Check if the request was successful
		return response.json()
