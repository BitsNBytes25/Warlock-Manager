from pathlib import Path


class PropertiesConfig:
    """Read and write Java-style .properties configuration files.

    Supports ``=`` and ``:`` as key/value separators and ``#``/``!`` comment
    prefixes.  Lines that contain neither ``=`` nor ``:`` are stored as keys
    with an empty-string value.
    """

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self._data: dict[str, str] = {}
        if self.filepath.exists():
            self._load()

    def _load(self) -> None:
        self._data.clear()
        with self.filepath.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith(("#", "!")):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                elif ":" in line:
                    key, _, value = line.partition(":")
                else:
                    self._data[line] = ""
                    continue
                self._data[key.strip()] = value.strip()

    def get(self, key: str, fallback: str = "") -> str:
        """Return the value for *key*, or *fallback* if the key is absent."""
        return self._data.get(key, fallback)

    def set(self, key: str, value: str) -> None:
        """Set *key* to *value*."""
        self._data[key] = value

    def keys(self) -> list[str]:
        """Return a list of all property keys."""
        return list(self._data.keys())

    def items(self) -> list[tuple[str, str]]:
        """Return a list of (key, value) pairs."""
        return list(self._data.items())

    def save(self) -> None:
        """Write the current configuration back to disk."""
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        with self.filepath.open("w", encoding="utf-8") as fh:
            for key, value in self._data.items():
                fh.write(f"{key}={value}\n")

    def __repr__(self) -> str:
        return f"PropertiesConfig(filepath={str(self.filepath)!r})"
