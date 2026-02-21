import configparser
from pathlib import Path


class IniConfig:
    """Read and write INI-format configuration files."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self._parser = configparser.ConfigParser()
        if self.filepath.exists():
            self._parser.read(self.filepath, encoding="utf-8")

    def get(self, section: str, key: str, fallback: str = "") -> str:
        """Return the value for *key* in *section*, or *fallback* if absent."""
        return self._parser.get(section, key, fallback=fallback)

    def set(self, section: str, key: str, value: str) -> None:
        """Set *key* to *value* in *section*, creating the section if needed."""
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, key, value)

    def has_section(self, section: str) -> bool:
        """Return True if *section* exists in the configuration."""
        return self._parser.has_section(section)

    def sections(self) -> list[str]:
        """Return a list of all sections."""
        return self._parser.sections()

    def options(self, section: str) -> list[str]:
        """Return a list of options in the given section."""
        return self._parser.options(section)

    def items(self, section: str) -> list[tuple[str, str]]:
        """Return a list of (key, value) pairs for *section*."""
        return self._parser.items(section)

    def save(self) -> None:
        """Write the current configuration back to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("w", encoding="utf-8") as fh:
            self._parser.write(fh)

    def __repr__(self) -> str:
        return f"IniConfig(filepath={str(self.filepath)!r})"
