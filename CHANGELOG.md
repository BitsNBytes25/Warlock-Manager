# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Add support for public profiles on https://warlock.nexus
- Add support for mod lookups from Curseforge
- Add "prompt_long_text" to TUI for entering a literal page of content
- Add skeleton for BaseService.get_ip (to allow them to be modified by the game)
- Add skeleton for BaseService.get_version
- Add skeleton for BaseService.get_loader (useful for Minecraft)
- Add support for services to push data to https://warlock.nexus
- Add support for hosts to be registered on https://warlock.nexus
- Add TUI for managing public community profile on https://warlock.nexus
- Add BaseMod.get_mod to retrieve a single mod by its ID
- Add CLI API for get_mods for a given service
- Add CLI API for install_mod for a given service
- Add CLI API for remove_mod for a given service
- Add support for provider source in mods
- Add BaseMod.is_same to compare mods ignoring their version
- Add skeleton for BaseMod.calculate_files for generating the list of files to be installed
- Add support for defining the provider for WarlockNexusMods.get_mod
- Add BaseService.install_mod_dependencies for installing dependencies of a mod
- Add BaseService.remove_mod_files for removing files associated with a mod
- Add BaseService.get_mod for retrieving an enabled mod
- Add BaseService.check_mod_files_installed for checking if a mod's files are installed
- Add BaseService.install_mod_files for installing files associated with a mod

### Changed

- Modify installer to set up host authentication key for https://warlock.nexus
- Modify installer to set up container for user email for https://warlock.nexus
- Modify installer to store game GUID in the management directory
- Overhaul mod TUI to be more user friendly
- Add lock icons in TUI for features which cannot be changed (eg: game is running)
- BaseMod.find_mod now requires the service as the first parameter
- Show mod provider source instead of URL in TUI mods list
- Add support for int-based mod IDs (Curseforge uses ints)
- Change mod file listing to be a dict instead of list to support zip archives
- Populate BaseMod.find_mods to support pulling manually installed mods
- Populate BaseMod.get_mod to support pulling manually installed mods
- Add version and loader to data returned from service lookups

### Deprecated

### Removed

### Fixed

### Security


## [2.1.2] - 2026-03-28

### Added

- Add interface for managing game mods


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

- **v2.1.2**: Add support for mod management in the CLI application
- **v2.1.1**: Versioning by tracking the commit hash during installation
- **v2.1.0**: CLI application for managing Warlock-compatible games
- **v2.0.4**: Backport versioning by tracking the commit hash during installation
- **v2.0.3**: Backport deployment to PyPI
- **v2.0.2**: Minor bug fixes for process status handling
- **v2.0.1**: Socket support and port detection enhancements  
- **v2.0.0**: Major API redesign with service-level operations
- **v1.0.0**: Initial release with core functionality

[2.1.2]: https://pypi.org/project/warlock-manager/2.1.2
[2.1.1]: https://pypi.org/project/warlock-manager/2.1.1
[2.1.0]: https://pypi.org/project/warlock-manager/2.1.0
[2.0.4]: https://pypi.org/project/warlock-manager/2.0.4
[2.0.3]: https://pypi.org/project/warlock-manager/2.0.3