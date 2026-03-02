Configuration System
====================

Warlock-Manager provides a flexible configuration system supporting multiple file formats. This guide explains how to use each configuration type.

Overview
--------

The configuration system is built around the `BaseConfig` abstract class, which provides:

- Option definition and management
- Type conversion and validation
- Load/save functionality
- Default value handling
- File existence checking

Supported Formats
-----------------

- **INI**: Windows .ini format with sections and key=value pairs
- **JSON**: Structured JSON format
- **Properties**: Java properties format (key=value)
- **Unreal**: Unreal Engine .ini format with special syntax
- **CLI**: Command-line arguments and flags

Using Configuration in Your App
-------------------------------

### Adding Configurations to BaseApp

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.config.ini_config import INIConfig
from warlock_manager.config.json_config import JSONConfig

class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "MyGame"
        
        # Add config files
        self.configs['game'] = INIConfig(
            'mygame_game',
            '/etc/mygame/game.ini'
        )
        self.configs['settings'] = JSONConfig(
            'mygame_settings',
            '/etc/mygame/settings.json'
        )
    
    def load(self):
        """Load all configs"""
        super().load()
```

### Adding Configurations to BaseService

```python
from warlock_manager.services.base_service import BaseService
from warlock_manager.config.ini_config import INIConfig

class MyGameService(BaseService):
    def __init__(self, service: str, game):
        super().__init__(service, game)
        
        # Add instance-specific configs
        self.configs['instance'] = INIConfig(
            'mygame_instance',
            f'/opt/mygame/{service}/instance.ini'
        )
        
        self.load()
```

INI Configuration
-----------------

Traditional Windows-style .ini files with sections.

**File Format:**
```ini
[Section1]
key1=value1
key2=value2

[Section2]
key3=value3
```

**Usage:**
```python
from warlock_manager.config.ini_config import INIConfig

config = INIConfig('myapp', '/path/to/config.ini')
config.add_option(
    name='max_players',
    section='Game',
    key='MaxPlayers',
    default='32',
    val_type='int',
    help_text='Maximum number of players'
)

config.load()
value = config.get_value('max_players')  # Returns: 32 (as int)
config.set_value('max_players', 64)
config.save()
```

JSON Configuration
------------------

Structured JSON format for complex nested configurations.

**File Format:**
```json
{
  "game": {
    "name": "MyGame",
    "max_players": 32,
    "difficulty": 1.5
  },
  "network": {
    "port": 8080,
    "enable_ssl": true
  }
}
```

**Usage:**
```python
from warlock_manager.config.json_config import JSONConfig

config = JSONConfig('myapp', '/path/to/config.json')
config.add_option(
    name='max_players',
    section='game',
    key='max_players',
    default='32',
    val_type='int'
)

config.load()
value = config.get_value('max_players')
config.save()
```

Properties Configuration
------------------------

Java properties format (simple key=value lines).

**File Format:**
```properties
# Comment
max_players=32
server_name=MyServer
enable_pvp=true
```

**Usage:**
```python
from warlock_manager.config.properties_config import PropertiesConfig

config = PropertiesConfig('myapp', '/path/to/server.properties')
config.add_option(
    name='max_players',
    section='',
    key='max_players',
    default='32',
    val_type='int'
)

config.load()
value = config.get_value('max_players')
config.save()
```

Unreal Engine Configuration
---------------------------

Specialized format for Unreal Engine .ini files with support for:
- Array notation: `key=(Item1,Item2,Item3)`
- Struct notation: `key=(X=1,Y=2,Z=3)`
- Complex nested structures
- Array operators like `+=`, `-=`

**File Format:**
```ini
[/Script/Engine.GameEngine]
bUseFixedFrameRate=True
FixedFrameRate=60

[/Script/MyGame.MyGameMode]
MaxPlayers=32
DifficultyOffset=1.5
SpawnPoints=(X=100,Y=200,Z=50),(X=300,Y=400,Z=50)
```

**Usage:**
```python
from warlock_manager.config.unreal_config import UnrealConfig

config = UnrealConfig('myapp', '/path/to/config.ini')
config.add_option(
    name='max_players',
    section='/Script/MyGame.MyGameMode',
    key='MaxPlayers',
    default='32',
    val_type='int'
)

config.load()
value = config.get_value('max_players')
config.save()
```

**Advanced: Working with Arrays and Structs:**
```python
# Unreal config handles complex types automatically
config.add_option(
    name='spawn_points',
    section='/Script/MyGame.MyGameMode',
    key='SpawnPoints',
    val_type='str'  # Returns raw value
)

# Get raw spawn point data
spawn_data = config.get_value('spawn_points')
# Returns: [(X=100,Y=200,Z=50),(X=300,Y=400,Z=50)]
```

CLI Configuration
-----------------

Command-line argument handling for application launch configurations.

**File Format (optional - can be format-less):**
```bash
#!/bin/bash
./game_server [OPTIONS]
```

**Usage:**
```python
from warlock_manager.config.cli_config import CLIConfig

config = CLIConfig(
    'myapp',
    '/etc/myapp/launch.sh'
)
config.add_option(
    name='port',
    section='',
    key='-port',
    default='8080',
    val_type='int'
)
config.add_option(
    name='server_name',
    section='',
    key='-name',
    default='MyServer',
    val_type='str'
)

config.load()
port = config.get_value('port')
config.save()
```

Option Management
-----------------

### Adding Options

```python
config.add_option(
    name='max_players',              # Unique identifier
    section='Game',                   # Config section (not used in Properties)
    key='MaxPlayers',                 # Actual key in file
    default='32',                     # Default value
    val_type='int',                   # Type: str, int, bool
    help_text='Maximum players',      # Description
    options=None                      # Optional: list of allowed values
)
```

### Getting Values

```python
# Get current value (uses default if not set)
value = config.get_value('max_players')  # Returns: 32 (as int)

# Get default value
default = config.get_default('max_players')  # Returns: '32' (as str)

# Get all options
options = config.get_options()  # Returns: list of option names
```

### Setting Values

```python
# Set a value
config.set_value('max_players', 64)

# Save changes to file
config.save()
```

### Type Conversion

Options are defined with types that are enforced on load/save:

```python
# Define a boolean option
config.add_option(
    name='enable_pvp',
    section='Game',
    key='EnablePVP',
    default='True',
    val_type='bool'
)

# Values are returned as proper Python types
enable_pvp = config.get_value('enable_pvp')  # Returns: True (bool)
```

Working with Missing Files
---------------------------

All config classes handle missing files gracefully:

```python
config = INIConfig('myapp', '/nonexistent/path.ini')

# Check if file exists before loading
if config.exists():
    config.load()
else:
    print("Config file not found, using defaults")

# You can still use default values
value = config.get_value('some_option')  # Returns default value
```

Configuration in BaseApp/BaseService
-------------------------------------

Both `BaseApp` and `BaseService` provide convenience methods:

```python
# In your app or service:
app.load()  # Loads all registered configs

# Get options across all configs
all_options = app.get_options()

# Get a value from any config
value = app.get_option_value('some_option')

# Set a value (sets in correct config automatically)
app.set_option('some_option', 'new_value')

# Save all configs
app.save()
```

Config Validation
-----------------

For basic validation, use the `options` parameter:

```python
config.add_option(
    name='difficulty',
    section='Game',
    key='Difficulty',
    default='Normal',
    val_type='str',
    options=['Easy', 'Normal', 'Hard']  # Only these values allowed
)

# This will only accept one of the specified values
config.set_value('difficulty', 'Hard')  # OK
config.set_value('difficulty', 'Invalid')  # Will raise error or use default
```

Common Patterns
---------------

### Game with Multiple Config Files

```python
class MyGame(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "MyGame"
        
        # Different format for different config types
        self.configs['server'] = INIConfig(
            'mygame_server',
            '/etc/mygame/server.ini'
        )
        self.configs['player'] = JSONConfig(
            'mygame_player',
            '/etc/mygame/players.json'
        )
        self.configs['launch'] = CLIConfig(
            'mygame_launch',
            '/etc/mygame/launch.sh'
        )
```

### Service with Instance-Specific Config

```python
class MyGameService(BaseService):
    def __init__(self, service: str, game):
        super().__init__(service, game)
        
        # Config path includes service name for multi-instance
        self.configs['instance'] = INIConfig(
            'mygame_instance',
            f'/opt/mygame/{service}/config.ini'
        )
```

### Conditional Configuration Loading

```python
def load(self):
    for config in self.configs.values():
        if config.exists():
            config.load()
    
    # Custom validation/processing
    if self.get_option_value('enable_feature'):
        # Do something
        pass
```

Best Practices
--------------

1. **Define options at initialization** - Add all options in __init__, not dynamically
2. **Use consistent naming** - Name your options clearly and consistently
3. **Provide sensible defaults** - Always have default values defined
4. **Validate option ranges** - Check min/max values after loading
5. **Use appropriate types** - Choose int, str, or bool correctly
6. **Document requirements** - Add help_text explaining what each option does
7. **Handle file changes** - Reload configs if files change on disk
8. **Catch save errors** - Handle cases where file writes fail

See Also
--------

- :ref:`api/config:Config Module` - API reference for all config classes
- :doc:`extending-baseapp` - Using configs in BaseApp
- :doc:`implementing-services` - Using configs in BaseService

