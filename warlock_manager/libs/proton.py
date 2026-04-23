from warlock_manager.libs.cmd import Cmd


def get_proton_paths() -> list[str]:
	"""
	Get a list of all Proton executable paths available on the system using alternatives.

	:return: A list of paths to Proton executables
	"""

	# Try update-alternatives first (Debian-based distros)
	cmd = Cmd(['update-alternatives', '--list', 'proton'])
	if cmd.success:
		return cmd.lines

	# Fall back to alternatives (RHEL-based distros)
	cmd = Cmd(['alternatives', '--list', 'proton'])
	if cmd.success:
		return [line.split()[2] for line in cmd.lines]

	return []
