# Warlock Manager

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/warlock-manager)
[![PyPI - Version](https://img.shields.io/pypi/v/warlock-manager)](https://pypi.org/project/warlock-manager/)

Warlock Manager is a robust, extensible Python library for building game server management applications. It provides a comprehensive foundation for managing game applications, services, configurations, and server communications.

This is meant to be used with the [Warlock Game Manager](https://warlock.nexus) ([Github Repo](https://github.com/BitsNBytes25/Warlock)),
but can be used independently.

> **Note:** This is a dependency library designed to be integrated into game server manager applications. It is not intended to be used standalone.

## Overview

Warlock Manager abstracts common game server management tasks, allowing you to build specialized manager applications for various games. It handles:

- **Application Management**: Base classes for managing game applications and multiple service instances
- **Configuration Handling**: Unified configuration system supporting multiple formats (INI, JSON, YAML, Properties, Unreal Engine)
- **Service Management**: Integration with systemd for service creation, control, and monitoring
- **Network Communication**: Multiple protocols (HTTP, RCON, Socket) for server interaction
- **CLI Tools**: Built-in CLI utilities for common operations
- **TUI Interface**: Terminal user interface components for interactive management

## Features

### Core Components

- **BaseApp**: Abstract base for game application managers
    - Multi-service instance support
    - Service lifecycle management
    - Configuration management
    - Update handling

- **BaseService**: Abstract base for game service instances
    - systemd integration
    - Configuration file management
    - Port management and firewall integration
    - Player count and status monitoring
    - Backup and restore capabilities
    - Command execution and API communication

- **Configuration System**: Multiple configuration format support
    - `BaseConfig`: Abstract configuration handler
    - `IniConfig`: INI file support
    - `JsonConfig`: JSON file support
    - `PropertiesConfig`: Java properties file support
    - `UnrealConfig`: Unreal Engine configuration format
    - `CliConfig`: Command-line argument configuration

- **Service Protocols**:
    - `HttpService`: HTTP-based server communication
    - `RconService`: RCON protocol support
    - `SocketService`: Unix socket-based communication

### Utilities

- **CLI Framework**: Built on Typer for robust command-line interfaces
- **Terminal UI**: Menu systems and formatted output for interactive terminals
- **Command Execution**: Background and foreground process management
- **Firewall Management**: Automatic firewall rule configuration
- **Port Management**: Port discovery, allocation, and validation
- **Data Filtering**: Sensitive data masking for safe logging

## Installation

Install as a dependency in your project:

```bash
pip install warlock-manager
```

Or add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "warlock-manager>=2.1.0",
]
```

Or to your `requirements.txt`:

```
warlock-manager>=2.1.0
```

## Requirements

- Python 3.10+
- Dependencies:
    - `requests>=2.28` - HTTP client library
    - `pyyaml>=6.0` - YAML parsing
    - `typer>=0.24.1` - CLI framework
    - `rcon>=2.4.9` - RCON protocol support
    - `systemdunitparser>=0.4` - systemd unit file parsing
    - `packaging>=23.3` - Version handling
    - `psutil>=7.2.0` - System process utilities

## Quick Start

### Creating a Game Manager

For more detailed examples, check out the [Warlock Game Template](https://github.com/BitsNBytes25/Warlock-Game-Template)
repository for a templated project you can fork and customize to quickly get started.

Extend `BaseApp` to create a manager for your game:

```python
from warlock_manager.apps import BaseApp
from warlock_manager.services import BaseService

class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = 'mygame'
        self.desc = 'My Game Server'
        self.service_prefix = 'mygame-'
        
    def get_app_directory(self) -> str:
        return '/var/games/mygame'
    
    def detect_services(self) -> list:
        # Detect existing game services
        return []
    
    def create_service(self, name: str) -> BaseService:
        # Create and return a new service instance
        pass
```

### Creating a Game Service Handler

Extend `BaseService` to implement service-specific logic:

```python
from warlock_manager.services import BaseService
from warlock_manager.config import IniConfig

class MyGameService(BaseService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        
        # Configure configuration files
        self.configs['game_config'] = IniConfig(
            '/var/games/mygame/game.ini'
        )
    
    def get_port_definitions(self) -> list:
        # Return list of port definitions: (port_number_or_config_key, 'tcp'/'udp', description)
        return [
            ('game_port', 'tcp', 'Game Server Port'),
            ('query_port', 'udp', 'Query Port'),
        ]
    
    def is_running(self) -> bool:
        # Check if service is running
        pass
```

### Building a CLI Application

Use the built-in CLI framework:

```python
from warlock_manager.libs.app_runner import app_runner

game = MyGameApp()
cli_app = app_runner(game)

if __name__ == '__main__':
    cli_app()
```

This automatically provides commands for:
- Service management (start, stop, restart, status)
- Configuration management (get, set)
- Port discovery and management
- Metrics collection
- Backup and restore operations
- First-run setup


Additionally, the included TUI application as provided by app provides an interactive menu system for:

This provides an interactive menu system for:
- Viewing service status and metrics
- Managing service configurations
- Controlling service lifecycle
- Backup and data management
- Creating new service instances

## Configuration

Configuration files can be defined through YAML (`configs.yaml`) in your application's `scripts/` directory. Each configuration option specifies:

- Section: INI section or logical grouping
- Key: Configuration option name
- Default value
- Type: str, int, or bool
- Help text
- Display group

Example `configs.yaml`:

```yaml
mygame:
  - section: "Game Settings"
    key: "server_name"
    default: "My Server"
    type: "str"
    help: "The name of the game server"
    group: Basic
  
  - section: "Network"
    key: "game_port"
    default: "27015"
    type: "int"
    help: "Game server port"
    group: Network
```

## Features System

Control available functionality through the features system:

```python
class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        
        # Available features
        self.features = {
            'api',              # Server API support
            'cmd',              # Command execution via API
            'create_service',   # Create new service instances
            'mods',             # Mod support
        }
        
        # Disable specific features
        self.disabled_features = {'mods'}
```

Available features:
- `api` - Server API communication support
- `cmd` - Command execution capabilities
- `create_service` - Ability to create new service instances
- `mods` - Mod/plugin support

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/BitsNBytes25/Warlock-Manager.git
cd warlock-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=warlock_manager
```

### Code Quality

Run linting checks:

```bash
flake8 warlock_manager tests
```

## API Reference

### BaseApp

Main application class for game server management.

**Key Methods:**
- `detect_services()`: Discover existing service instances
- `create_service(name)`: Create a new service instance
- `get_services()`: Get list of service instances
- `get_options()`: Get application-level configuration options
- `get_option_value(key)`: Get a configuration option value
- `set_option(key, value)`: Set a configuration option
- `start_all()`: Start all service instances
- `stop_all()`: Stop all service instances
- `is_active()`: Check if any service is running
- `update()`: Update the application/game

### BaseService

Service instance handler for individual game servers.

**Key Methods:**
- `load()`: Load service configuration files
- `get_options()`: Get service configuration options
- `get_option_value(key)`: Get a configuration option
- `set_option(key, value)`: Set a configuration option
- `start()`: Start the service
- `stop()`: Stop the service
- `restart()`: Restart the service
- `is_running()`: Check if service is running
- `get_port()`: Get service's primary port
- `get_ports()`: Get all port definitions
- `is_enabled()`: Check if auto-start is enabled
- `cmd(command)`: Send command to service
- `get_player_count()`: Get current player count
- `get_player_max()`: Get max player capacity
- `backup()`: Create backup of service data
- `restore(backup_path)`: Restore from backup

### Configuration Classes

All configuration classes extend `BaseConfig` and provide:
- `load()`: Load configuration from file
- `save()`: Save configuration to file
- `get_option_value(key)`: Get option value
- `set_option_value(key, value)`: Set option value
- `exists()`: Check if configuration file exists

## License

This project is licensed under the GNU Affero General Public License v3.0 or later - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure:

1. Code follows PEP 8 style guidelines (checked with flake8)
2. All tests pass (`pytest`)
3. New features include appropriate tests
4. Documentation is updated

## Support

For issues, questions, and suggestions, please visit the project repository or refer to the documentation.

---

Built with ❤️ for game server administrators

