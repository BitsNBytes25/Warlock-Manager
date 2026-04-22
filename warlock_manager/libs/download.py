import logging
import requests
import json
from warlock_manager.libs import utils
from warlock_manager.libs import cache
from warlock_manager.libs.meta import get_meta

# "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
USER_AGENT = 'Warlock Manager/%s (warlock.nexus) <staff@bitsnbytes.dev>' % get_meta()['version']


def download_file(url: str, destination: str):
    """
    Download a file from a URL to a destination path.

    :param game: The game instance, used to set ownership of the downloaded file
    :param url: The URL to download from
    :param destination: The local file path to save the downloaded file to
    :return:
    """
    logging.debug('Downloading file %s to %s' % (url, destination))
    # Ensure the target directory exists
    utils.ensure_file_parent_exists(destination)

    response = requests.get(url, stream=True, headers={'User-Agent': USER_AGENT})
    response.raise_for_status()  # Check if the request was successful

    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Once complete, set ownership for the downloaded file
    utils.ensure_file_ownership(destination)


def download_json(url: str) -> dict:
    """
    Download JSON data from a URL and return it as a dictionary.

    This method supports caching, so the result is cached to disk,
    and subsequent calls pull from that cache for a time.

    :param game: The game instance, used to set ownership of the downloaded file
    :param url: The URL to download from
    :return: The JSON data as a dictionary
    """
    logging.debug('Downloading JSON %s' % url)

    # Try the cache first
    cached = cache.get_cache(url)
    if cached is not None:
        return json.loads(cached)

    response = requests.get(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
    response.raise_for_status()  # Check if the request was successful
    data = response.json()

    cache.save_cache(url, json.dumps(data))
    return data
