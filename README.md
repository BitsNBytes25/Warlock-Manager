# Warlock-Manager

A comprehensive dependency library for game-server management applications. Warlock-Manager provides abstractions for managing game configurations, services, and utilities across multiple game platforms.

## Features

- **Game Application Management**: Define and manage game server instances with a flexible framework
- **Service Management**: Control systemd services with abstraction layers for different API types
- **Configuration Handling**: Parse and manage configuration files in multiple formats (INI, JSON, Unreal Engine, CLI, Properties)
- **API Communication**: Interact with game servers via HTTP, RCON, or Socket APIs
- **Firewall Management**: Automatically manage firewall rules for opened ports (UFW, Firewalld, iptables)
- **Utilities**: Network utilities, text UI helpers, and CLI app builder for game server management

## Installation

Install from PyPI:

```bash
pip install warlock-manager
```

Or with development dependencies:

```bash
pip install warlock-manager[dev,docs]
```

## Quick Start

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService

# Create your game app
class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "My Game"
        self.services = ['game-1']
        self.service_handler = MyGameService

# Implement the service
class MyGameService(BaseService):
    def __init__(self, service: str, game: MyGameApp):
        super().__init__(service, game)
        self.load()

# Use it
game = MyGameApp()
service = game.get_service('game-1')
print(f"Service running: {service.is_running()}")
```

## Documentation

Full documentation is available in the `docs/` directory and includes:

- **Getting Started**: Introduction and quick-start guide
- **User Guides**: 
  - Extending `BaseApp` for your game
  - Implementing custom `BaseService` classes
  - Configuration system for multiple file formats
  - Utility libraries (Firewall, TUI, Network)
- **API Reference**: Complete autodoc API documentation generated from source

### Building Documentation Locally

Prerequisites:

```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints myst-parser
```

Build HTML documentation:

```bash
cd docs
make html
```

View the documentation:

```bash
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
start _build/html/index.html  # Windows
```

Watch for changes and auto-rebuild (requires `sphinx-autobuild`):

```bash
pip install sphinx-autobuild
cd docs
make livehtml
```

### Online Documentation

Documentation is automatically generated and deployed on every commit. See the GitHub Pages deployment for the latest version.

## Architecture

### BaseApp

Represents a game application and manages:
- Game metadata (name, description)
- Service instances
- Configuration files
- Game-level options interface

### BaseService

Represents a running game server instance and provides:
- Service status monitoring (running, stopped, etc.)
- API communication (HTTP, RCON, Socket)
- Port and firewall management
- Player and server statistics

### Configuration System

Supports multiple file formats:
- **INI**: Windows .ini format
- **JSON**: Structured JSON configuration
- **Properties**: Java properties format
- **Unreal**: Specialized Unreal Engine .ini parsing
- **CLI**: Command-line argument management

### Utility Libraries

- **Firewall**: Manage firewall rules across UFW, Firewalld, iptables
- **TUI**: Build text user interfaces
- **Network**: Get external IP addresses
- **App Runner**: Build CLI applications with Typer

## Supported Games

This library is designed to be flexible and support any game server. It's currently used for:

- Ark: Survival Evolved
- Minecraft
- Valheim
- Palworld
- Custom Unreal Engine applications

## Development

### Running Tests

```bash
pip install pytest pytest-mock responses
pytest
```

### Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest`
2. Code follows style guidelines: `flake8`
3. New features include docstrings and tests
4. Documentation is updated

## License

Licensed under the GNU Affero General Public License v3 (AGPL-3.0). See `LICENSE` file for details.

This means:
- ✅ You can use, modify, and distribute this software
- ✅ You must share modifications and derivatives
- ✅ If you offer this as a service, you must share the source code

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Changelog

See `CHANGELOG.md` for version history and breaking changes.

---

**Built for game server management automation.**
