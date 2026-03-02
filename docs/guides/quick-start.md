Quick Start
===========

Installation
------------

Install Warlock-Manager from PyPI:

```bash
pip install warlock-manager
```

For development with documentation support:

```bash
pip install warlock-manager[docs,dev]
```

Basic Usage
-----------

### Creating a Custom Game Application

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.services.base_service import BaseService
from warlock_manager.config.cli_config import CLIConfig

class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "MyGame"
        self.desc = "My Game Server Manager"
        self.service_handler = MyGameService
        self.services = ['mygame']
        
        # Add configuration files
        self.configs['cli'] = CLIConfig('mygame_cli', '/path/to/launch.sh')

class MyGameService(BaseService):
    def __init__(self, service: str, game: MyGameApp):
        super().__init__(service, game)
        # Initialize service-specific configs here
        self.load()
```

### Managing Services

```python
# Create your game app
game = MyGameApp()
game.load()

# Get all services
services = game.get_services()

# Get a specific service
service = game.get_service('mygame')

# Check if service is running
if service.is_running():
    print("Server is running!")
    
# Get player count (if implemented)
players = service.get_player_count()
```

### Working with Configuration

```python
# Get configuration options
options = game.get_options()
print("Available options:", options)

# Get an option value
max_players = game.get_option_value('max_players')

# Set an option value
game.set_option('max_players', 50)

# Save configuration
game.save()
```

### Using Utilities

#### Network Utilities

```python
from warlock_manager.libs.get_wan_ip import get_wan_ip

wan_ip = get_wan_ip()
print(f"Server WAN IP: {wan_ip}")
```

#### Firewall Management

```python
from warlock_manager.libs.firewall import Firewall

# Check what firewall is available
firewall = Firewall.get_available()
print(f"Available firewall: {firewall}")

# Allow a port
Firewall.allow(8080, 'tcp', 'MyGame Server')

# Remove a firewall rule
Firewall.remove(8080, 'tcp')
```

#### Text User Interface

```python
from warlock_manager.libs.tui import print_header, prompt_yn, prompt_text

# Print a formatted header
print_header("Game Server Manager", width=60, clear=True)

# Yes/No prompt
if prompt_yn("Start server now?", default='y'):
    print("Starting server...")

# Text input
server_name = prompt_text("Enter server name: ", default="MyServer", prefill=True)
```

Next Steps
----------

- Learn how to extend :doc:`extending-baseapp` for your game
- Implement custom :doc:`implementing-services` with API support
- Understand the :doc:`configuration` system
- Explore :doc:`utilities` available in the library

