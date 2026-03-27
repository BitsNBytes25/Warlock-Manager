# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Add interface for managing game mods

### Changed

### Deprecated

### Removed

### Fixed

### Security


## [2.1.1] - 2026-03-25

### Added

- Update install_warlock_manager to use PyPI if a version number is specified instead of a branch name
- Add version tracking by logging the commit hash during installation

### Changed

- Use testPyPi only on pushes to release-* branches


## [2.0.4] - 2026-03-25

### Added

- Backport version tracking by logging the commit hash during installation


## [2.0.3] - 2026-03-25

### Changed

- Backport deployment to PyPI
- Backport install_warlock_manager to use PyPI if a version number is specified instead of a branch name


## [2.1.0] - 2026-03-25

### Added

- CLI application port for managing Warlock-compatible games
- Support for `wipe` and `mod` features in CLI
- Port status checking for all game ports via `get_port_status()`
- Global firewall open checking via `Firewall.is_global_open()` 
- Post-startup port checking to monitor when game ports become available
- Memory caching implementation for commands (e.g., systemctl checks)
- Support for psutil-based port detection in Build 2.1+
- Support for retrieving current Steam branches
- Implemented a TUI for interactive management from the CLI

### Changed

- Updated CLI port title formatting for improved aesthetics
- Added subtitle support to CLI formatter
- Refactored socket watcher to use two threads (loader and handler) for more consistent results
- `save` endpoint now uses `get_save_directory()` to support games with saves outside the application directory
- Updated project URLs configuration in pyproject.toml

### Deprecated

- BaseApp.get_app_directory (use get_app_directory() from utils instead)
- BaseApp.get_home_directory (use get_home_directory() from utils instead)
- BaseApp.get_app_uid (use get_app_uid() from utils instead)
- BaseApp.get_app_gid (use get_app_gid() from utils instead)
- BaseApp.ensure_file_ownership (use ensure_file_ownership() from utils instead)
- BaseApp.ensure_file_parent_exists (use ensure_file_parent_exists() from utils instead)
- BaseApp.makedirs (use makedirs() from utils instead)

### Fixed

- PyPI deployment workflow issues
- Dependency resolution in GitHub workflows
- Port-related configuration issues
- CLI formatter refactoring and utilities
- Project configuration and documentation in README

## [2.0.2] - 2026-03-21

### Fixed

- Handle "failed" status as valid for `is_stopped()` check

## [2.0.1] - 2026-03-20

### Added

- Socket watch support for faster status monitoring
- Socket creation/removal handling
- Version bump utilities and functions

### Changed

- Updated socket implementation to provide faster results
- Better process handling when the process is not running

### Fixed

- Port conflict detection improvements for new services
- Directory structure creation for configs

## [2.0.0] - 2026-03-18

### Added

- Complete rewrite with major API improvements
- Support for service-level update and check-update operations
- Backup and restore functionality at the service level
- New command handler (`cmd`) for executing raw commands
- Service removal functionality with configuration cleanup
- Feature enablement/disablement on a per-game basis
- Support for creating directories while ensuring correct permissions
- Cache support for JSON downloads
- Service daemon-reload as built-in functionality
- Java detection library
- Support for manual apps and per-instance installs
- API module with v1 endpoints

### Changed

- Breaking changes to configuration handling with new display groups
- Services changed from dictionary to list format
- CLI generation functionality migrated to standalone formatter for cross-config handler support
- Steam backend optimizations and startup timeout resolution
- Download utilities moved to standalone library for individual inclusion
- Main branch now points to latest release instead of cherry-picking approach

### Fixed

- ConfigKey handling for empty string values (type coercion)
- Service creation with optimal port conflict detection
- Home directory determination using file owner instead of current user
- Service backup operations with optional service parameter
- Logging improvements and sensitive data handling
- IDE hinting for services
- Internal service handling to reduce external dependencies
- Flake8 linting and pre-commit unit tests
- Configuration key handling with support for default values
- Service prefix enablement prior to service creation
- Firewall management integration from upstream project

## [1.0.0] - 2026-02-21

### Added

- Initial release of Warlock Manager
- BaseApp and SteamApp classes for application management
- BaseService, HttpService, and RconService implementations
- IniConfig and PropertiesConfig configuration handlers
- Socket-based service support
- Pip-installable package distribution
- GitHub Actions CI/CD setup
- Project documentation and licensing

---

## Development Notes

This project is under active development. For the latest features and bug fixes, please refer to the [main branch](https://github.com/your-repo/Warlock-Manager).

### Key Architecture Components

- **Apps**: Manages application configurations and lifecycle
- **Services**: Handles service-level operations and communication
- **Config**: Configuration file parsing and management
- **Libs**: Utility libraries for common operations
- **Formatters**: CLI output formatting and presentation

### Version History Summary

- **v2.0.2**: Minor bug fixes for process status handling
- **v2.0.1**: Socket support and port detection enhancements  
- **v2.0.0**: Major API redesign with service-level operations
- **v1.0.0**: Initial release with core functionality

