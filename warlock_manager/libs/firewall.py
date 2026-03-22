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
			ufw_check = Cmd(['ufw', 'status'])
			ufw_check.is_memory_cacheable(3)
			if 'Status: active' in ufw_check.text:
				return 'ufw'
		except FileNotFoundError:
			pass

		# Check for Firewalld
		try:
			firewalld_check = Cmd(['firewall-cmd', '--state'])
			firewalld_check.is_memory_cacheable(3)
			if 'running' in firewalld_check.text:
				return 'firewalld'
		except FileNotFoundError:
			pass

		# Check for iptables
		try:
			iptables_check = Cmd(['iptables', '-L'])
			iptables_check.is_memory_cacheable(3)
			if iptables_check.success:
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
		ufw_check = Cmd(['ufw', '--version'])
		ufw_check.is_memory_cacheable(3)
		if ufw_check.success:
			return 'ufw'

		# Check for Firewalld
		firewalld_check = Cmd(['firewall-cmd', '--version'])
		firewalld_check.is_memory_cacheable(3)
		if firewalld_check.success:
			return 'firewalld'

		# Check for iptables
		iptables_check = Cmd(['iptables', '--version'])
		iptables_check.is_memory_cacheable(3)
		if iptables_check.success:
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

	@classmethod
	def is_global_open(cls, port: int, protocol: str = 'tcp') -> bool:
		"""
		Checks if a specific port is open in the system's firewall.
		Supports UFW, Firewalld, and iptables.

		This checks if the source host is global and not a specific host.

		Args:
			port (int): The port number to check.
			protocol (str, optional): The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.
		"""

		firewall = cls.get_enabled()

		if firewall is None:
			# No firewall is enabled, assume it's open
			return True

		elif firewall == 'ufw':
			# UFW: look for "ALLOW" for the port/protocol from "Anywhere"
			ufw_check = Cmd(['ufw', 'status'])
			ufw_check.is_memory_cacheable(3)
			result = ufw_check.text
			port_proto = f"{port}/{protocol}"
			for line in result.splitlines():
				if port_proto in line and "ALLOW" in line and ("Anywhere" in line or "Anywhere (v6)" in line):
					return True
			return False

		elif firewall == 'firewalld':
			# Firewalld: check if port/protocol is listed in --list-ports
			firewalld_check = Cmd(['firewall-cmd', '--list-ports'])
			firewalld_check.is_memory_cacheable(3)
			result = firewalld_check.text
			port_proto = f"{port}/{protocol}"
			return port_proto in result.split()

		elif firewall == 'iptables':
			# iptables: look for ACCEPT rule for port/protocol from 0.0.0.0/0
			iptables_check = Cmd(['iptables', '-L', 'INPUT', '-n'])
			iptables_check.is_memory_cacheable(3)
			result = iptables_check.text
			for line in result.splitlines():
				if "ACCEPT" in line and protocol in line and str(port) in line and ("0.0.0.0/0" in line or "anywhere" in line):
					return True
			return False

		else:
			raise OSError("No supported firewall found on the system.")
