# Warlock Manager

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/warlock-manager)
[![PyPI - Version](https://img.shields.io/pypi/v/warlock-manager)](https://pypi.org/project/warlock-manager/)

Warlock Manager is a robust, extensible Python library for building game server management applications. 
It provides a comprehensive foundation for managing game applications, services, configurations, and server communications.

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

In this system, a game is defined as an 'Application' or 'App'.
This management library is meant to manage one single app to allow it be extended
to meet the requirements of that specific game.

A map or instance of the game is defined as a 'Service'.
Each service runs a single instance of the game executable.

An app will have one or more services, based on the game.
Some games support multiple services from a single game installation,
some support multiple services from multiple binaries,
and some only support a single instance.

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

- **Mod Support**:
  - `BaseMod`: Baseline mod class for basic functionality and skeleton structure
  - `WarlockNexusMod`: Support for pulling mod metadata from hosted [Warlock.Nexus](https://warlock.nexus)

### Utilities

- **CLI Framework**: Built on Typer for robust command-line interfaces
- **Terminal UI**: Menu systems and formatted output for interactive terminals
- **Command Execution**: Background and foreground process management
- **Firewall Management**: Automatic firewall rule configuration
- **Port Management**: Port discovery, allocation, and validation
- **Data Filtering**: Sensitive data masking for safe logging

### Default Features

This library automatically provides commands for:

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

## Installation

Install as a dependency in your project:

```bash
pip install warlock-manager
```

Or add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "warlock-manager>=2.2.0",
]
```

Or to your `requirements.txt`:

```
warlock-manager>=2.2.0
```

## Requirements

- Python 3.10+ (3.11+ recommended)
- Dependencies:
  - `requests>=2.28` - HTTP client library
  - `pyyaml>=6.0` - YAML parsing
  - `typer>=0.24.1` - CLI framework
  - `rcon>=2.4.9` - RCON protocol support
  - `systemdunitparser>=0.4` - systemd unit file parsing
  - `packaging>=23.3` - Version handling
  - `psutil>=7.2.0` - System process utilities

## Quick Start

For detailed examples, check out the [Warlock Game Template](https://github.com/BitsNBytes25/Warlock-Game-Template)
repository for a templated project you can fork and customize to quickly get started.

Also check out the games listed as supported at [Warlock.Nexus](https://warlock.nexus) 
to browse their source repos for more real-world implementations.

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

### Generating Documentation

Documentation is generated using [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown).

```bash
pydoc-markdown
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
