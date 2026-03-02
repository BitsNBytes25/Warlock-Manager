Introduction
=============

Warlock-Manager is a Python library designed to simplify game server management. It provides a flexible framework for:

- **Game Application Management**: Define and manage game server instances
- **Service Management**: Control systemd services with abstraction layers
- **Configuration Handling**: Parse and manage configuration files in multiple formats (INI, JSON, Unreal Engine, CLI)
- **API Communication**: Interact with game servers via HTTP, RCON, or Socket APIs
- **Firewall Management**: Automatically manage firewall rules for opened ports
- **Utilities**: Network utilities, TUI helpers, and app runner for CLI applications

Key Concepts
============

BaseApp
-------

A ``BaseApp`` represents a game application. It:

- Manages game-specific configurations
- Provides access to service instances
- Handles configuration loading and saving
- Defines option interfaces for game settings

BaseService
-----------

A ``BaseService`` represents a running game server instance. It:

- Manages instance-specific configurations
- Communicates with the game server via APIs (HTTP, RCON, Socket)
- Tracks service status (running, stopped, etc.)
- Provides access to game-specific data (players, stats, etc.)

Configuration System
--------------------

The configuration system supports:

- **INI Files**: Traditional Windows INI format
- **JSON**: Structured JSON configuration
- **Unreal Engine**: Specialized parsing for Unreal .ini files with custom syntax
- **Properties**: Java properties format
- **CLI Arguments**: Command-line argument flags and options

Use Cases
=========

Warlock-Manager is ideal for:

- Creating management dashboards for game servers
- Building automation tools for batch server operations
- Developing CLIs for game server management
- Building REST APIs for server administration
- Creating monitoring and alerting systems

Getting Started
===============

See the :doc:`quick-start` guide to begin using Warlock-Manager in your project.

