Implementing Services
=====================

`BaseService` is the core abstraction for managing individual game server instances. This guide shows you how to implement custom services.

Overview
--------

A `BaseService` subclass represents a single running game server instance. It provides:

- Instance-specific configuration management
- Service status monitoring (running, stopped, starting, stopping)
- API communication (HTTP, RCON, Socket)
- Port and firewall management
- Player and server stat tracking

Basic Implementation
--------------------

Here's a minimal service implementation:

```python
from warlock_manager.services.base_service import BaseService
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.config.properties_config import PropertiesConfig

class MinecraftService(BaseService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        
        # Add service-specific configurations
        self.configs['properties'] = PropertiesConfig(
            'minecraft_props',
            f'/opt/minecraft/{service}/server.properties'
        )
        
        # Load configurations
        self.load()
```

Service Status Methods
---------------------

Implement these abstract methods to track service status:

```python
class MinecraftService(BaseService):
    # ...existing code...
    
    def is_running(self) -> bool:
        """Check if the service process is running"""
        # Implementation depends on how you detect running state
        # Common: check systemd, check PID file, check port listening
        pass
    
    def is_starting(self) -> bool:
        """Check if the service is in starting state"""
        pass
    
    def is_stopping(self) -> bool:
        """Check if the service is in stopping state"""
        pass
    
    def is_stopped(self) -> bool:
        """Check if the service is stopped"""
        return not self.is_running()
```

API Communication
-----------------

Implement API methods depending on how your game server communicates:

### RCON (Remote Console)

For games supporting RCON (Minecraft, CS:GO, etc.):

```python
from warlock_manager.services.rcon_service import RCONService

class MinecraftService(RCONService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        self.configs['properties'] = PropertiesConfig(...)
        self.load()
    
    def get_api_port(self) -> int | None:
        """Return RCON port from config"""
        return int(self.get_option_value('rcon_port'))
    
    def get_api_password(self) -> str | None:
        """Return RCON password from config"""
        return self.get_option_value('rcon_password')
    
    def get_api_enabled(self) -> bool:
        """Check if RCON is enabled"""
        return self.get_option_value('enable_rcon')
    
    def get_players(self) -> list | None:
        """Get list of connected players"""
        response = self._api_cmd('list')
        if not response:
            return None
        # Parse player list from response
        lines = response.split('\n')
        return [line.strip() for line in lines if line.strip()]
```

### HTTP REST API

For games with HTTP API (Valheim Plus, some modded servers):

```python
from warlock_manager.services.http_service import HTTPService

class ValheimService(HTTPService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        self.configs['launch'] = CLIConfig(...)
        self.load()
    
    def get_api_port(self) -> int | None:
        """Return HTTP API port"""
        return int(self.get_option_value('api_port'))
    
    def get_api_enabled(self) -> bool:
        """Check if HTTP API is enabled"""
        return self.get_option_value('enable_api')
    
    def get_api_password(self) -> str | None:
        """Return API password if required"""
        return self.get_option_value('api_password', '')
    
    def get_api_username(self) -> str | None:
        """Return API username if required"""
        return None
    
    def get_server_status(self) -> dict | None:
        """Get server status via HTTP API"""
        return self._api_cmd('/status', method='GET')
    
    def get_players(self) -> list | None:
        """Get connected players"""
        response = self._api_cmd('/players', method='GET')
        if response and 'players' in response:
            return response['players']
        return None
```

### Socket API

For games communicating via Unix sockets:

```python
from warlock_manager.services.socket_service import SocketService

class CustomGameService(SocketService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        # Override socket path if needed
        self.socket = f'/var/run/{service}.sock'
        self.load()
    
    def is_api_enabled(self) -> bool:
        """Check if socket exists and is accessible"""
        return super().is_api_enabled()
    
    def get_server_info(self) -> dict | None:
        """Get server info via socket"""
        self._api_cmd('STATUS')
        # Parse response as needed
        return None
```

Port Management
---------------

Implement port definitions for your service:

```python
class MinecraftService(BaseService):
    # ...existing code...
    
    def get_port_definitions(self) -> list:
        """
        Return list of ports used by this service
        
        Each port is a tuple: (port_number, protocol, description)
        """
        return [
            (25565, 'tcp', 'Minecraft Server'),
            (25565, 'udp', 'Minecraft Server UDP'),
        ]
    
    def get_ports_enabled_firewall(self) -> dict:
        """Get which ports are currently enabled in firewall"""
        from warlock_manager.libs.firewall import Firewall
        
        firewall = Firewall.get_enabled()
        enabled = {}
        
        for port, protocol, desc in self.get_port_definitions():
            # Implementation depends on firewall type
            enabled[f"{port}/{protocol}"] = self._port_allowed(port, protocol)
        
        return enabled
```

Gamedata and Stats
------------------

Implement methods to retrieve game-specific data:

```python
class MinecraftService(BaseService):
    # ...existing code...
    
    def get_player_count(self) -> int | None:
        """Get current number of connected players"""
        players = self.get_players()
        return len(players) if players else None
    
    def get_max_players(self) -> int:
        """Get max allowed players"""
        return int(self.get_option_value('max_players'))
    
    def get_world_name(self) -> str:
        """Get the world/level name"""
        return self.get_option_value('level_name')
    
    def get_game_mode(self) -> str:
        """Get game mode (Survival, Creative, Adventure)"""
        return self.get_option_value('gamemode')
    
    def get_difficulty(self) -> str:
        """Get difficulty level"""
        return self.get_option_value('difficulty')
```

Server Control Commands
-----------------------

Implement methods to control the server:

```python
class MinecraftService(BaseService):
    # ...existing code...
    
    def start(self) -> bool:
        """Start the game server"""
        # Implementation: systemctl start, direct process, etc.
        pass
    
    def stop(self) -> bool:
        """Stop the game server gracefully"""
        # Implementation: send shutdown command via RCON, systemctl stop, etc.
        pass
    
    def restart(self) -> bool:
        """Restart the game server"""
        if not self.stop():
            return False
        # Wait for full stop
        time.sleep(5)
        return self.start()
    
    def save(self) -> bool:
        """Save server state (if applicable)"""
        # Send save command via API
        response = self._api_cmd('save-all')
        return response is not None
    
    def send_message(self, message: str) -> bool:
        """Send a message to all players"""
        response = self._api_cmd(f'say {message}')
        return response is not None
```

Complete Example: Ark Service
-----------------------------

Here's a more complete example for an Ark server:

```python
from warlock_manager.services.rcon_service import RCONService
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.config.cli_config import CLIConfig

class ArkService(RCONService):
    def __init__(self, service: str, game: BaseApp):
        super().__init__(service, game)
        self.configs['launch'] = CLIConfig(
            'ark_launch',
            f'/etc/ark/{service}/launch.sh'
        )
        self.load()
    
    def get_api_port(self) -> int | None:
        """Get RCON port"""
        return int(self.get_option_value('rcon_port', 27020))
    
    def get_api_password(self) -> str | None:
        """Get RCON password"""
        return self.get_option_value('rcon_password', '')
    
    def get_api_enabled(self) -> bool:
        """RCON is always enabled for Ark"""
        return True
    
    def get_port_definitions(self) -> list:
        return [
            (7777, 'udp', 'Ark Game Server'),
            (7778, 'udp', 'Ark Query Port'),
            (27020, 'tcp', 'Ark RCON'),
        ]
    
    def get_players(self) -> list | None:
        """Get list of players - Ark format"""
        response = self._api_cmd('ListPlayers')
        if not response:
            return None
        # Parse Ark player list format
        return response.split('\n')[1:]
    
    def get_map_name(self) -> str:
        """Get current map"""
        response = self._api_cmd('GetChat')
        # Extract map from server info
        return "Unknown"
    
    def broadcast(self, message: str) -> bool:
        """Broadcast message to all players"""
        response = self._api_cmd(f'broadcast {message}')
        return response is not None
```

Best Practices
--------------

1. **Always call super().__init__()** and call `self.load()` at end of __init__
2. **Handle API unavailability gracefully** - return None instead of raising exceptions
3. **Implement status methods first** - they're used by other methods
4. **Cache expensive operations** - don't query player list on every call if possible
5. **Use type hints** - make your API clear to IDE and users
6. **Document port definitions** - make it clear what each port is for
7. **Implement get_name()** - return the service name for logging/display
8. **Handle connection errors** - don't crash if server is unreachable
9. **Use timeouts** - all API calls should have reasonable timeouts
10. **Thread safely** - if your service is used in async/multi-threaded context, use locks

See Also
--------

- :doc:`extending-baseapp` - Implement the game app class
- :doc:`configuration` - Learn about configuration file formats
- :ref:`api/services:BaseService` - API reference for BaseService class

