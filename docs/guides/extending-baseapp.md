Extending BaseApp
=================

`BaseApp` is the core abstraction for game applications. This guide shows you how to create custom game implementations.

Overview
--------

A `BaseApp` subclass represents a game and provides:

- Game metadata (name, description)
- Service instance management
- Configuration file management
- Option/setting interface for game-level config

Basic Implementation
--------------------

Here's a minimal example:

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService

class MinecraftApp(BaseApp):
    def __init__(self):
        super().__init__()
        # Game metadata
        self.name = "Minecraft"
        self.desc = "Minecraft Server Manager"
        
        # Reference the service class handler
        self.service_handler = MinecraftService
        
        # List of available service instances
        self.services = ['minecraft-1', 'minecraft-2']
```

Adding Configuration Files
---------------------------

Most games require configuration files. Add them in `__init__`:

```python
from warlock_manager.config.cli_config import CLIConfig
from warlock_manager.config.properties_config import PropertiesConfig

class MinecraftApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "Minecraft"
        self.desc = "Minecraft Server Manager"
        self.service_handler = MinecraftService
        self.services = ['minecraft-1', 'minecraft-2']
        
        # Add configuration files
        # Note: You'll need to resolve the actual paths for your setup
        self.configs['server_properties'] = PropertiesConfig(
            'minecraft_server',
            '/path/to/server.properties'
        )
        self.configs['eula'] = PropertiesConfig(
            'minecraft_eula',
            '/path/to/eula.txt'
        )

    def load(self):
        """Load all configuration files"""
        super().load()
        if self.configured:
            print(f"Loaded {self.name} configuration")

    def save(self):
        """Save all configuration files"""
        super().save()
        print(f"Saved {self.name} configuration")
```

Adding Custom Methods
---------------------

Extend `BaseApp` with game-specific functionality:

```python
class MinecraftApp(BaseApp):
    # ...existing code...
    
    def get_server_version(self) -> str:
        """Get the Minecraft server version"""
        # Custom logic to determine version
        return self.get_option_value('server_version')
    
    def get_max_players(self) -> int:
        """Get maximum players allowed"""
        return int(self.get_option_value('max_players'))
    
    def set_max_players(self, count: int) -> None:
        """Set maximum players allowed"""
        self.set_option('max_players', count)
    
    def get_difficulty(self) -> str:
        """Get game difficulty level"""
        return self.get_option_value('difficulty')
    
    def backup_world(self, backup_path: str) -> bool:
        """Create a world backup"""
        # Implement backup logic
        pass
```

Accessing Services from BaseApp
--------------------------------

The `BaseApp` class provides methods to access service instances:

```python
# Get all services
services = game.get_services()

# Get a specific service by name
service = game.get_service('minecraft-1')

# Interact with service
if service and service.is_running():
    # Send RCON command
    response = service.execute_command('say Hello world!')
```

Configuration Option Management
--------------------------------

`BaseApp` provides helper methods for managing options defined in config files:

```python
# Get list of all available options
options = game.get_options()
for opt in options:
    print(opt)

# Get current value
difficulty = game.get_option_value('difficulty')

# Get default value
default_difficulty = game.get_option_default('difficulty')

# Set option value
game.set_option('difficulty', 'hard')

# Save changes
game.save()
```

Complete Example: Ark Server
-----------------------------

Here's a more complete example for an Ark server:

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.config.unreal_config import UnrealConfig
from warlock_manager.config.cli_config import CLIConfig

class ArkApp(BaseApp):
    def __init__(self, instance: str = 'ark-1'):
        super().__init__()
        self.name = "Ark: Survival Evolved"
        self.desc = "Ark: Survival Evolved Server Manager"
        self.instance = instance
        self.service_handler = ArkService
        self.services = [instance]
        
        # Ark uses Unreal Engine config format
        self.configs['game'] = UnrealConfig(
            'ark_game',
            f'/etc/ark/{instance}/GameUserSettings.ini'
        )
        self.configs['engine'] = UnrealConfig(
            'ark_engine',
            f'/etc/ark/{instance}/Engine.ini'
        )
        self.configs['launch'] = CLIConfig(
            'ark_launch',
            f'/etc/ark/{instance}/launch.sh'
        )
    
    def get_difficulty(self) -> float:
        """Get game difficulty multiplier"""
        return float(self.get_option_value('DifficultyOffset'))
    
    def set_difficulty(self, difficulty: float) -> None:
        """Set game difficulty multiplier"""
        self.set_option('DifficultyOffset', str(difficulty))
    
    def get_map_name(self) -> str:
        """Get current map name"""
        return self.get_option_value('MapNameOverride')
    
    def restart_required(self) -> bool:
        """Check if server restart is required"""
        return any(config._is_changed for config in self.configs.values())
```

Best Practices
--------------

1. **Always call super().__init__()** at the start of your __init__ method
2. **Use descriptive names** for your game class and configs
3. **Document custom methods** with docstrings explaining what they do
4. **Validate option values** before setting them
5. **Handle configuration errors gracefully** - don't let one bad config crash the whole app
6. **Lazy load expensive operations** - only compute things when needed
7. **Make your service_handler flexible** - allow subclassing for different service types if needed

See Also
--------

- :doc:`implementing-services` - Implement the service class for your game
- :doc:`configuration` - Learn about configuration file formats
- :ref:`api/apps:BaseApp` - API reference for BaseApp class

