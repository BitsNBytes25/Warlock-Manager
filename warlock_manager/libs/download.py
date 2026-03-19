import requests
import hashlib
import time
import os
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from warlock_manager.apps.base_app import BaseApp


def download_file(game: 'BaseApp', url: str, destination: str):
    """
    Download a file from a URL to a destination path.

    :param game: The game instance, used to set ownership of the downloaded file
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
    game.ensure_file_ownership(destination)


def download_json(game: 'BaseApp', url: str) -> dict:
    """
    Download JSON data from a URL and return it as a dictionary.

    This method supports caching, so the result is cached to disk,
    and subsequent calls pull from that cache for a time.

    :param game: The game instance, used to set ownership of the downloaded file
    :param url: The URL to download from
    :return: The JSON data as a dictionary
    """
    # Ensure cache directory exists
    cache_path = os.path.join(game.get_app_directory(), '.cache')
    if not os.path.exists(cache_path):
        os.makedirs(cache_path)
        game.ensure_file_ownership(cache_path)

    # Check cache prior to downloading.
    url_hash = hashlib.sha256(url.encode()).hexdigest()
    cache_path = os.path.join(game.get_app_directory(), '.cache', url_hash)
    if os.path.exists(cache_path):
        if time.time() - os.path.getmtime(cache_path) < 3600:
            with open(cache_path, "r") as f:
                return json.load(f)

    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    data = response.json()
    with open(cache_path, "w") as f:
        json.dump(data, f)
    game.ensure_file_ownership(cache_path)
    return data
