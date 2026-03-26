class BaseMod:
	def __init__(self):
		self.name: str = ''
		"""
		Human-friendly name of this mod
		"""

		self.description: str | None = None
		"""
		Human-friendly description of this mod
		"""

		self.url: str | None = None
		"""
		Informative URL of this mod
		"""

		self.id: str | None = None
		"""
		Optional unique identifier for this mod
		"""

		self.author: str | None = None
		"""
		Author name and/or contact info for the author of this mod
		"""

		self.source: str | None = None
		"""
		Source URL to download this mod
		"""

		self.version: str | None = None
		"""
		Version of this mod
		"""

		self.package: str | None = None
		"""
		Base package filename of this mod file, generally the source archive
		"""

		self.dependencies: list[str] | None = None
		"""
		List of mod dependencies
		"""

		self.files: list[str] | None = None
		"""
		List of files installed in the game path
		"""
