import os
import pwd
import sys
import random
from typing_extensions import deprecated
from warlock_manager.libs.logger import logger


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

		logger.debug('Ensuring ownership of %s to %s:%s' % (file, uid, gid))
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
	if not (target_dir.startswith(get_base_directory()) or target_dir.startswith(get_home_directory())):
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


def random_string(length: int = 12) -> str:
	"""
	Generate a random string consisting of letters and numbers of a given length.

	Similarly-looking characters such as "0" and "O" are excluded.

	:param length:
	:return:
	"""
	choices = 'abcdefghjkmoprstuvwxyzABCDEFGHJKMNPQSTUVWXYZ23456789'
	return ''.join(random.choices(choices, k=length))


def random_passphrase() -> str:
	"""
	https://xkcd.com/936/

	:return:
	"""
	passphrase_adjectives = [
		"Abundant", "Brave", "Cheerful", "Dazzling", "Ethereal",
		"Fierce", "Grand", "Humble", "Joyful", "Kindred",
		"Luminous", "Majestic", "Noble", "Opulent", "Pristine",
		"Quirky", "Radiant", "Serene", "Triumphant", "Vibrant",
		"Wondrous", "Zealous", "Agile", "Bold", "Calm", "Dreamy",
		"Enchanting", "Fluffy", "Gleaming", "Heroic", "Intense",
		"Jubilant", "Kindly", "Lovely", "Mystic", "Perfect",
		"Splendid", "Thrilling", "Unique", "Vivid", "Wise", "Correct"
	]

	passphrase_animal = [
		"Lion", "Tiger", "Elephant", "Bear", "Wolf", "Cheetah",
		"Eagle", "Falcon", "Hawk", "Owl", "Deer", "Stag",
		"Zebra", "Giraffe", "Kangaroo", "Monkey", "Chimpanzee",
		"Panda", "Rhinoceros", "Hippopotamus", "Crocodile",
		"Snake", "Dragon", "Fox", "Rabbit", "Squirrel", "Badger",
		"Dolphin", "Whale", "Shark", "Octopus", "Parrot",
		"Penguin", "Koala", "Leopard", "Jaguar", "Gorilla",
		"Viper", "Horse"
	]
	passphrase_noun = [
		"Mountain", "Ocean", "Forest", "River", "Sky", "Star", "Moon", "Planet", "Battery",
		"Cloud", "Stone", "Tree", "Flower", "Leaf", "Sun", "Wind", "Rain",
		"Fire", "Water", "Earth", "Time", "Dream", "Idea", "Memory", "Thought",
		"City", "House", "Castle", "Tower", "Bridge", "Road", "Path", "Valley",
		"Island", "Desert", "Sand", "Rock", "Metal", "Gold", "Silver", "Jewel",
		"Book", "Page", "Pen", "Ink", "Key", "Lock", "Door", "Window",
		"Music", "Sound", "Note", "Chord", "Rhythm", "Shadow", "Light", "Echo",
		"Spirit", "Soul", "Heart", "Mind", "Power", "Force", "Magic", "Energy",
		"Galaxy", "Comet", "Meteor", "Atom", "Molecule", "Planetoid", "Orbit", "Vortex"
	]
	passphrase_game = [
		"Sword", "Potion", "Shield", "Mana", "Health", "Gold", "XP", "Scroll", "Gem", "Key", "Staple",
		"Dragon", "Goblin", "Orc", "Elf", "Wizard", "Armor", "Weapon", "Map", "Quest", "Loot",
		"Boss", "Dungeon", "Castle", "Tower", "Crystal", "Amulet", "Rune", "Spell", "Grind", "Relic",
		"Portal", "Gems", "Elixir", "Scrolls", "Map", "Staff", "Warlock", "Town", "Ring", "Forest"
	]

	return ''.join([
		random.choice(passphrase_adjectives),
		random.choice(passphrase_animal),
		random.choice(passphrase_noun),
		random.choice(passphrase_game)
	])
