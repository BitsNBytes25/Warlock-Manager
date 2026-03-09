from warlock_manager.libs.cmd import Cmd


class Firewall:
	"""
	Simple utility class for managing firewall rules on the system.

	Supports UFW, Firewalld, and iptables.
	Provides methods to check for enabled and available firewalls, as well as to allow and remove specific ports.
	"""

	@classmethod
	def get_enabled(cls) -> str | None:
		"""
		Returns the name of the enabled firewall on the system.
		Checks for UFW, Firewalld, and iptables in that order.

		Returns:
			str: The name of the enabled firewall ('ufw', 'firewalld', 'iptables') or None if none are enabled.
		"""

		# Check for UFW
		try:
			if 'Status: active' in Cmd(['ufw', 'status']).text:
				return 'ufw'
		except FileNotFoundError:
			pass

		# Check for Firewalld
		try:
			if 'running' in Cmd(['firewall-cmd', '--state']).text:
				return 'firewalld'
		except FileNotFoundError:
			pass

		# Check for iptables
		try:
			if Cmd(['iptables', '-L']).success:
				return 'iptables'
		except FileNotFoundError:
			pass

		return None

	@classmethod
	def get_available(cls) -> str | None:
		"""
		Returns the name of the available firewall on the system.
		Checks for UFW, Firewalld, and iptables in that order.

		Returns:
			str: The name of the available firewall ('ufw', 'firewalld', 'iptables') or None if none are available.
		"""

		# Check for UFW
		if Cmd(['ufw', '--version']).success:
			return 'ufw'

		# Check for Firewalld
		if Cmd(['firewall-cmd', '--version']).success:
			return 'firewalld'

		# Check for iptables
		if Cmd(['iptables', '--version']).success:
			return 'iptables'

		return None

	@classmethod
	def allow(cls, port: int, protocol: str = 'tcp', comment: str = None) -> None:
		"""
		Allows a specific port through the system's firewall.
		Supports UFW, Firewalld, and iptables.

		Args:
			port (int): The port number to allow.
			protocol (str, optional): The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.
			comment (str, optional): An optional comment for the rule. Defaults to None.
		"""

		firewall = cls.get_available()

		if firewall == 'ufw':
			cmd = Cmd(['ufw', 'allow', f'{port}/{protocol}'])
			if comment:
				cmd.extend(['comment', comment])
			cmd.run()

		elif firewall == 'firewalld':
			Cmd(['firewall-cmd', '--permanent', '--add-port', f'{port}/{protocol}']).run()
			Cmd(['firewall-cmd', '--reload']).run()

		elif firewall == 'iptables':
			cmd = Cmd(['iptables', '-A', 'INPUT', '-p', protocol, '--dport', str(port), '-j', 'ACCEPT'])
			if comment:
				cmd.extend(['-m', 'comment', '--comment', comment])
			cmd.run()
			Cmd(['service', 'iptables', 'save']).run()

		else:
			raise OSError("No supported firewall found on the system.")

	@classmethod
	def remove(cls, port: int, protocol: str = 'tcp') -> None:
		"""
		Removes a specific port from the system's firewall.
		Supports UFW, Firewalld, and iptables.

		Args:
			port (int): The port number to remove.
			protocol (str, optional): The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.
		"""

		firewall = cls.get_available()

		if firewall == 'ufw':
			Cmd(['ufw', 'delete', 'allow', f'{port}/{protocol}']).run()

		elif firewall == 'firewalld':
			Cmd(['firewall-cmd', '--permanent', '--remove-port', f'{port}/{protocol}']).run()
			Cmd(['firewall-cmd', '--reload']).run()

		elif firewall == 'iptables':
			Cmd(['iptables', '-D', 'INPUT', '-p', protocol, '--dport', str(port), '-j', 'ACCEPT']).run()
			Cmd(['service', 'iptables', 'save']).run()

		else:
			raise OSError("No supported firewall found on the system.")
