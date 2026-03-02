Utilities Library
=================

Warlock-Manager provides several utility modules to simplify common tasks.

Firewall Management
-------------------

The `Firewall` class simplifies firewall rule management across different firewall backends (UFW, Firewalld, iptables).

### Basic Usage

```python
from warlock_manager.libs.firewall import Firewall

# Check what firewall is available on the system
firewall = Firewall.get_available()
print(f"Available firewall: {firewall}")  # ufw, firewalld, iptables, or None

# Check what firewall is currently enabled
enabled_firewall = Firewall.get_enabled()
print(f"Enabled firewall: {enabled_firewall}")
```

### Allowing Ports

```python
# Allow a TCP port
Firewall.allow(8080, 'tcp', 'Web Server')

# Allow a UDP port
Firewall.allow(53, 'udp', 'DNS Server')

# Allow both TCP and UDP on same port
Firewall.allow(5000, 'tcp', 'Game Server')
Firewall.allow(5000, 'udp', 'Game Server')
```

### Removing Rules

```python
# Remove TCP rule
Firewall.remove(8080, 'tcp')

# Remove UDP rule
Firewall.remove(53, 'udp')
```

### Error Handling

```python
try:
    Firewall.allow(8080, 'tcp', 'Web Server')
except FileNotFoundError:
    print("Firewall not available on this system")
```

### In Your Service

```python
from warlock_manager.services.base_service import BaseService
from warlock_manager.libs.firewall import Firewall

class MyGameService(BaseService):
    def __init__(self, service: str, game):
        super().__init__(service, game)
        self.load()
    
    def open_firewall(self) -> bool:
        """Open firewall ports for this service"""
        try:
            for port, protocol, desc in self.get_port_definitions():
                Firewall.allow(port, protocol, desc)
            return True
        except FileNotFoundError:
            print(f"No firewall available to open port {port}")
            return False
    
    def close_firewall(self) -> bool:
        """Close firewall ports for this service"""
        try:
            for port, protocol, desc in self.get_port_definitions():
                Firewall.remove(port, protocol)
            return True
        except FileNotFoundError:
            print(f"No firewall available to close port {port}")
            return False
```

Text User Interface (TUI)
------------------------

The `tui` module provides utilities for building command-line interfaces.

### Print Headers

```python
from warlock_manager.libs.tui import print_header

# Simple header
print_header("Game Server Manager")

# Customized header
print_header("⚙️  Configuration", width=60, clear=True)

# With clear (useful for menu screens)
print_header("Main Menu", width=80, clear=True)
```

**Output:**
```
================================================================================
                        Game Server Manager
================================================================================
```

### Text Input

```python
from warlock_manager.libs.tui import prompt_text

# Simple prompt
server_name = prompt_text("Enter server name: ")

# With default value
server_name = prompt_text(
    "Enter server name: ",
    default="MyServer"
)

# Prefill with default (editable)
server_name = prompt_text(
    "Enter server name: ",
    default="MyServer",
    prefill=True
)
```

### Yes/No Prompts

```python
from warlock_manager.libs.tui import prompt_yn

# Simple yes/no question
if prompt_yn("Start server now?"):
    print("Starting...")

# With default
if prompt_yn("Enable PVP?", default='n'):
    print("PVP enabled")
```

### Building a Menu

```python
from warlock_manager.libs.tui import print_header, prompt_text

def show_menu():
    while True:
        print_header("Game Server Manager", clear=True)
        print("1. Start Server")
        print("2. Stop Server")
        print("3. Restart Server")
        print("4. Exit")
        
        choice = prompt_text("Select option (1-4): ")
        
        if choice == '1':
            start_server()
        elif choice == '2':
            stop_server()
        elif choice == '3':
            restart_server()
        elif choice == '4':
            break
```

Network Utilities
-----------------

The `get_wan_ip` module provides utilities to determine your external IP address.

### Getting WAN IP

```python
from warlock_manager.libs.get_wan_ip import get_wan_ip

# Get external IP address
wan_ip = get_wan_ip()

if wan_ip:
    print(f"Your server's external IP: {wan_ip}")
else:
    print("Could not determine external IP")
```

### Use Cases

```python
from warlock_manager.libs.get_wan_ip import get_wan_ip

class MyGameService(BaseService):
    def get_connection_info(self) -> dict:
        """Get connection info for players"""
        wan_ip = get_wan_ip()
        port = self.get_api_port()
        
        return {
            'ip': wan_ip,
            'port': port,
            'url': f"{wan_ip}:{port}"
        }
```

App Runner (CLI Builder)
------------------------

The `app_runner` module helps build CLI applications using Typer for game server management.

### Basic CLI Setup

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.libs.app_runner import app_runner

class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "MyGame"
        self.services = ['game-1', 'game-2']

# Create CLI app
game = MyGameApp()
cli = app_runner(game)

if __name__ == '__main__':
    cli()
```

### Building CLI Commands

The `app_runner` function handles:
- Service instance selection (optional/required)
- Common options (debug logging)
- Command registration
- Error handling

```python
# Generated CLI structure:
# python cli.py --help
# python cli.py --debug start --service game-1
# python cli.py status --service game-1
# python cli.py list-players
```

### Custom Commands

```python
from warlock_manager.libs.app_runner import app_runner

game = MyGameApp()
app = app_runner(game)

@app.command()
def start(service: str = None):
    """Start a game server"""
    svc = game.get_service(service) if service else game.get_services()[0]
    if svc.start():
        print(f"Started {svc.service}")
    else:
        print(f"Failed to start {svc.service}")

@app.command()
def status(service: str = None):
    """Show server status"""
    services = [game.get_service(service)] if service else game.get_services()
    for svc in services:
        state = "RUNNING" if svc.is_running() else "STOPPED"
        print(f"{svc.service}: {state}")

if __name__ == '__main__':
    app()
```

Common Patterns
---------------

### Full CLI Application

```python
from warlock_manager.apps.base_app import BaseApp
from warlock_manager.libs.app_runner import app_runner
from warlock_manager.libs.tui import print_header
from warlock_manager.libs.get_wan_ip import get_wan_ip
from warlock_manager.libs.firewall import Firewall

class MyGameApp(BaseApp):
    def __init__(self):
        super().__init__()
        self.name = "MyGame"
        self.services = ['game-1']

game = MyGameApp()
game.load()
app = app_runner(game)

@app.command()
def info(service: str = None):
    """Show server information"""
    print_header("Server Information")
    svc = game.get_service(service) if service else game.get_services()[0]
    
    print(f"Service: {svc.service}")
    print(f"Status: {'RUNNING' if svc.is_running() else 'STOPPED'}")
    print(f"Max Players: {svc.get_max_players()}")
    print(f"Connected Players: {svc.get_player_count()}")
    
    wan_ip = get_wan_ip()
    if wan_ip:
        print(f"Connection: {wan_ip}:{svc.get_api_port()}")

@app.command()
def firewall():
    """Manage firewall rules"""
    print_header("Firewall Management")
    
    if not Firewall.get_available():
        print("No compatible firewall found")
        return
    
    svc = game.get_services()[0]
    
    if prompt_yn("Open firewall ports?"):
        try:
            svc.open_firewall()
            print("Firewall rules added")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    app()
```

Best Practices
--------------

1. **Check for firewall availability** before trying to allow/remove ports
2. **Handle missing WAN IP gracefully** - not all servers have public IPs
3. **Use headers for menu navigation** - improves UX
4. **Always provide defaults** - make CLI user-friendly
5. **Catch and display errors** - don't let exceptions crash the CLI
6. **Use appropriate prompts** - `prompt_yn` for yes/no, `prompt_text` for input
7. **Test on target systems** - ensure firewall compatibility with your targets

See Also
--------

- :ref:`api/libs:Libs Module` - Full API reference for all utility modules
- :doc:`quick-start` - Using utilities in your project

