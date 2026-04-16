# Table of Contents

* [\_\_init\_\_](#__init__)
* [mods](#mods)
* [mods.base\_mod](#mods.base_mod)
  * [BaseMod](#mods.base_mod.BaseMod)
    * [to\_dict](#mods.base_mod.BaseMod.to_dict)
    * [from\_dict](#mods.base_mod.BaseMod.from_dict)
    * [\_\_str\_\_](#mods.base_mod.BaseMod.__str__)
    * [\_\_eq\_\_](#mods.base_mod.BaseMod.__eq__)
    * [is\_same](#mods.base_mod.BaseMod.is_same)
    * [calculate\_files](#mods.base_mod.BaseMod.calculate_files)
    * [register](#mods.base_mod.BaseMod.register)
    * [download](#mods.base_mod.BaseMod.download)
    * [find\_mods](#mods.base_mod.BaseMod.find_mods)
    * [get\_mod](#mods.base_mod.BaseMod.get_mod)
    * [get\_registered\_mods](#mods.base_mod.BaseMod.get_registered_mods)
    * [save\_registered\_mods](#mods.base_mod.BaseMod.save_registered_mods)
* [mods.warlock\_nexus\_mod](#mods.warlock_nexus_mod)
  * [WarlockNexusMod](#mods.warlock_nexus_mod.WarlockNexusMod)
    * [find\_mods](#mods.warlock_nexus_mod.WarlockNexusMod.find_mods)
    * [get\_mod](#mods.warlock_nexus_mod.WarlockNexusMod.get_mod)
* [formatters](#formatters)
* [formatters.cli\_formatter](#formatters.cli_formatter)
* [libs](#libs)
* [libs.meta](#libs.meta)
  * [get\_meta](#libs.meta.get_meta)
* [libs.version](#libs.version)
  * [parse\_version](#libs.version.parse_version)
  * [compare\_versions](#libs.version.compare_versions)
  * [is\_version\_newer](#libs.version.is_version_newer)
  * [is\_version\_older](#libs.version.is_version_older)
  * [is\_version\_equal](#libs.version.is_version_equal)
  * [get\_major\_version](#libs.version.get_major_version)
  * [get\_minor\_version](#libs.version.get_minor_version)
  * [get\_patch\_version](#libs.version.get_patch_version)
  * [is\_prerelease](#libs.version.is_prerelease)
  * [is\_postrelease](#libs.version.is_postrelease)
  * [is\_devrelease](#libs.version.is_devrelease)
  * [extract\_version\_from\_string](#libs.version.extract_version_from_string)
  * [normalize\_version](#libs.version.normalize_version)
  * [get\_version\_distance](#libs.version.get_version_distance)
  * [is\_version\_compatible](#libs.version.is_version_compatible)
* [libs.app](#libs.app)
  * [menu\_public\_auth](#libs.app.menu_public_auth)
* [libs.cmd](#libs.cmd)
  * [CmdFakeResponse](#libs.cmd.CmdFakeResponse)
  * [Cmd](#libs.cmd.Cmd)
    * [\_\_init\_\_](#libs.cmd.Cmd.__init__)
    * [sudo](#libs.cmd.Cmd.sudo)
    * [use\_stdout](#libs.cmd.Cmd.use_stdout)
    * [use\_stderr](#libs.cmd.Cmd.use_stderr)
    * [stream\_output](#libs.cmd.Cmd.stream_output)
    * [is\_cacheable](#libs.cmd.Cmd.is_cacheable)
    * [is\_memory\_cacheable](#libs.cmd.Cmd.is_memory_cacheable)
    * [exists](#libs.cmd.Cmd.exists)
    * [text](#libs.cmd.Cmd.text)
    * [lines](#libs.cmd.Cmd.lines)
    * [json](#libs.cmd.Cmd.json)
    * [success](#libs.cmd.Cmd.success)
    * [exit\_status](#libs.cmd.Cmd.exit_status)
    * [run](#libs.cmd.Cmd.run)
    * [extend](#libs.cmd.Cmd.extend)
    * [append](#libs.cmd.Cmd.append)
  * [BackgroundCmd](#libs.cmd.BackgroundCmd)
    * [run](#libs.cmd.BackgroundCmd.run)
* [libs.utils](#libs.utils)
  * [get\_app\_directory](#libs.utils.get_app_directory)
  * [get\_home\_directory](#libs.utils.get_home_directory)
  * [get\_app\_uid](#libs.utils.get_app_uid)
  * [get\_app\_gid](#libs.utils.get_app_gid)
  * [ensure\_file\_ownership](#libs.utils.ensure_file_ownership)
  * [ensure\_file\_parent\_exists](#libs.utils.ensure_file_parent_exists)
  * [makedirs](#libs.utils.makedirs)
* [libs.app\_runner](#libs.app_runner)
* [libs.get\_wan\_ip](#libs.get_wan_ip)
  * [get\_wan\_ip](#libs.get_wan_ip.get_wan_ip)
* [libs.tui](#libs.tui)
  * [print\_header](#libs.tui.print_header)
  * [get\_terminal\_width](#libs.tui.get_terminal_width)
  * [prompt\_long\_text](#libs.tui.prompt_long_text)
  * [prompt\_text](#libs.tui.prompt_text)
  * [prompt\_yn](#libs.tui.prompt_yn)
  * [prompt\_options](#libs.tui.prompt_options)
  * [Table](#libs.tui.Table)
    * [\_\_init\_\_](#libs.tui.Table.__init__)
    * [render](#libs.tui.Table.render)
* [libs.sensitive\_data\_filter](#libs.sensitive_data_filter)
* [libs.firewall](#libs.firewall)
  * [Firewall](#libs.firewall.Firewall)
    * [get\_enabled](#libs.firewall.Firewall.get_enabled)
    * [get\_available](#libs.firewall.Firewall.get_available)
    * [allow](#libs.firewall.Firewall.allow)
    * [remove](#libs.firewall.Firewall.remove)
    * [is\_global\_open](#libs.firewall.Firewall.is_global_open)
* [libs.ports](#libs.ports)
  * [get\_listening\_port](#libs.ports.get_listening_port)
  * [get\_ports](#libs.ports.get_ports)
* [libs.cache](#libs.cache)
* [libs.download](#libs.download)
  * [download\_file](#libs.download.download_file)
  * [download\_json](#libs.download.download_json)
* [libs.java](#libs.java)
  * [get\_java\_paths](#libs.java.get_java_paths)
  * [find\_java\_version](#libs.java.find_java_version)
* [services](#services)
* [services.socket\_service](#services.socket_service)
  * [SocketService](#services.socket_service.SocketService)
    * [create\_service](#services.socket_service.SocketService.create_service)
    * [cmd](#services.socket_service.SocketService.cmd)
    * [write\_socket](#services.socket_service.SocketService.write_socket)
    * [watch](#services.socket_service.SocketService.watch)
    * [is\_api\_enabled](#services.socket_service.SocketService.is_api_enabled)
    * [get\_systemd\_config](#services.socket_service.SocketService.get_systemd_config)
    * [remove\_service](#services.socket_service.SocketService.remove_service)
* [services.http\_service](#services.http_service)
  * [HTTPService](#services.http_service.HTTPService)
    * [cmd](#services.http_service.HTTPService.cmd)
    * [is\_api\_enabled](#services.http_service.HTTPService.is_api_enabled)
    * [get\_api\_port](#services.http_service.HTTPService.get_api_port)
    * [get\_api\_password](#services.http_service.HTTPService.get_api_password)
    * [get\_api\_username](#services.http_service.HTTPService.get_api_username)
* [services.base\_service](#services.base_service)
  * [BaseService](#services.base_service.BaseService)
    * [\_\_init\_\_](#services.base_service.BaseService.__init__)
    * [load](#services.base_service.BaseService.load)
    * [get\_options](#services.base_service.BaseService.get_options)
    * [get\_option\_value](#services.base_service.BaseService.get_option_value)
    * [get\_option\_default](#services.base_service.BaseService.get_option_default)
    * [get\_option\_type](#services.base_service.BaseService.get_option_type)
    * [get\_option\_help](#services.base_service.BaseService.get_option_help)
    * [option\_value\_updated](#services.base_service.BaseService.option_value_updated)
    * [get\_option\_group](#services.base_service.BaseService.get_option_group)
    * [set\_option](#services.base_service.BaseService.set_option)
    * [option\_has\_value](#services.base_service.BaseService.option_has_value)
    * [get\_option\_options](#services.base_service.BaseService.get_option_options)
    * [option\_ensure\_set](#services.base_service.BaseService.option_ensure_set)
    * [get\_name](#services.base_service.BaseService.get_name)
    * [get\_ip](#services.base_service.BaseService.get_ip)
    * [get\_port](#services.base_service.BaseService.get_port)
    * [get\_port\_protocol](#services.base_service.BaseService.get_port_protocol)
    * [prompt\_option](#services.base_service.BaseService.prompt_option)
    * [get\_player\_max](#services.base_service.BaseService.get_player_max)
    * [get\_player\_count](#services.base_service.BaseService.get_player_count)
    * [get\_players](#services.base_service.BaseService.get_players)
    * [get\_pid](#services.base_service.BaseService.get_pid)
    * [get\_process\_status](#services.base_service.BaseService.get_process_status)
    * [get\_game\_pid](#services.base_service.BaseService.get_game_pid)
    * [get\_memory\_usage](#services.base_service.BaseService.get_memory_usage)
    * [get\_cpu\_usage](#services.base_service.BaseService.get_cpu_usage)
    * [get\_exec\_start\_status](#services.base_service.BaseService.get_exec_start_status)
    * [get\_exec\_start\_pre\_status](#services.base_service.BaseService.get_exec_start_pre_status)
    * [is\_enabled](#services.base_service.BaseService.is_enabled)
    * [is\_running](#services.base_service.BaseService.is_running)
    * [is\_starting](#services.base_service.BaseService.is_starting)
    * [is\_stopping](#services.base_service.BaseService.is_stopping)
    * [is\_stopped](#services.base_service.BaseService.is_stopped)
    * [is\_api\_enabled](#services.base_service.BaseService.is_api_enabled)
    * [is\_port\_open](#services.base_service.BaseService.is_port_open)
    * [enable](#services.base_service.BaseService.enable)
    * [disable](#services.base_service.BaseService.disable)
    * [print\_logs](#services.base_service.BaseService.print_logs)
    * [get\_logs](#services.base_service.BaseService.get_logs)
    * [send\_message](#services.base_service.BaseService.send_message)
    * [save\_world](#services.base_service.BaseService.save_world)
    * [get\_port\_definitions](#services.base_service.BaseService.get_port_definitions)
    * [get\_ports](#services.base_service.BaseService.get_ports)
    * [start](#services.base_service.BaseService.start)
    * [pre\_stop](#services.base_service.BaseService.pre_stop)
    * [post\_start](#services.base_service.BaseService.post_start)
    * [stop](#services.base_service.BaseService.stop)
    * [delayed\_stop](#services.base_service.BaseService.delayed_stop)
    * [restart](#services.base_service.BaseService.restart)
    * [delayed\_restart](#services.base_service.BaseService.delayed_restart)
    * [reload](#services.base_service.BaseService.reload)
    * [check\_update\_available](#services.base_service.BaseService.check_update_available)
    * [update](#services.base_service.BaseService.update)
    * [delayed\_update](#services.base_service.BaseService.delayed_update)
    * [post\_update](#services.base_service.BaseService.post_update)
    * [cmd](#services.base_service.BaseService.cmd)
    * [get\_commands](#services.base_service.BaseService.get_commands)
    * [get\_systemd\_config](#services.base_service.BaseService.get_systemd_config)
    * [get\_app\_directory](#services.base_service.BaseService.get_app_directory)
    * [get\_save\_directory](#services.base_service.BaseService.get_save_directory)
    * [get\_backup\_directory](#services.base_service.BaseService.get_backup_directory)
    * [get\_environment](#services.base_service.BaseService.get_environment)
    * [get\_info](#services.base_service.BaseService.get_info)
    * [build\_systemd\_config](#services.base_service.BaseService.build_systemd_config)
    * [create\_service](#services.base_service.BaseService.create_service)
    * [remove\_service](#services.base_service.BaseService.remove_service)
    * [get\_executable](#services.base_service.BaseService.get_executable)
    * [get\_save\_files](#services.base_service.BaseService.get_save_files)
    * [backup](#services.base_service.BaseService.backup)
    * [prepare\_backup](#services.base_service.BaseService.prepare_backup)
    * [complete\_backup](#services.base_service.BaseService.complete_backup)
    * [restore](#services.base_service.BaseService.restore)
    * [prepare\_restore](#services.base_service.BaseService.prepare_restore)
    * [complete\_restore](#services.base_service.BaseService.complete_restore)
    * [wipe](#services.base_service.BaseService.wipe)
    * [get\_enabled\_mods](#services.base_service.BaseService.get_enabled_mods)
    * [add\_mod](#services.base_service.BaseService.add_mod)
    * [install\_mod\_dependencies](#services.base_service.BaseService.install_mod_dependencies)
    * [remove\_mod](#services.base_service.BaseService.remove_mod)
    * [remove\_mod\_files](#services.base_service.BaseService.remove_mod_files)
    * [get\_mod](#services.base_service.BaseService.get_mod)
    * [check\_mod\_files\_installed](#services.base_service.BaseService.check_mod_files_installed)
    * [install\_mod\_files](#services.base_service.BaseService.install_mod_files)
    * [get\_version](#services.base_service.BaseService.get_version)
    * [get\_loader](#services.base_service.BaseService.get_loader)
* [services.rcon\_service](#services.rcon_service)
  * [RCONService](#services.rcon_service.RCONService)
    * [cmd](#services.rcon_service.RCONService.cmd)
    * [get\_player\_count](#services.rcon_service.RCONService.get_player_count)
    * [is\_api\_enabled](#services.rcon_service.RCONService.is_api_enabled)
    * [get\_api\_port](#services.rcon_service.RCONService.get_api_port)
    * [get\_api\_password](#services.rcon_service.RCONService.get_api_password)
* [apps](#apps)
* [apps.steam\_app](#apps.steam_app)
  * [steamcmd\_parse\_manifest](#apps.steam_app.steamcmd_parse_manifest)
  * [SteamApp](#apps.steam_app.SteamApp)
    * [get\_app\_details](#apps.steam_app.SteamApp.get_app_details)
    * [get\_steam\_branches](#apps.steam_app.SteamApp.get_steam_branches)
    * [check\_update\_available](#apps.steam_app.SteamApp.check_update_available)
    * [update](#apps.steam_app.SteamApp.update)
* [apps.manual\_app](#apps.manual_app)
  * [ManualApp](#apps.manual_app.ManualApp)
    * [get\_latest\_version](#apps.manual_app.ManualApp.get_latest_version)
    * [download\_file](#apps.manual_app.ManualApp.download_file)
    * [download\_json](#apps.manual_app.ManualApp.download_json)
* [apps.base\_app](#apps.base_app)
  * [BaseApp](#apps.base_app.BaseApp)
    * [load](#apps.base_app.BaseApp.load)
    * [save](#apps.base_app.BaseApp.save)
    * [get\_options](#apps.base_app.BaseApp.get_options)
    * [get\_option\_value](#apps.base_app.BaseApp.get_option_value)
    * [get\_option\_default](#apps.base_app.BaseApp.get_option_default)
    * [get\_option\_type](#apps.base_app.BaseApp.get_option_type)
    * [get\_option\_help](#apps.base_app.BaseApp.get_option_help)
    * [option\_value\_updated](#apps.base_app.BaseApp.option_value_updated)
    * [set\_option](#apps.base_app.BaseApp.set_option)
    * [get\_option\_options](#apps.base_app.BaseApp.get_option_options)
    * [get\_option\_group](#apps.base_app.BaseApp.get_option_group)
    * [prompt\_option](#apps.base_app.BaseApp.prompt_option)
    * [is\_active](#apps.base_app.BaseApp.is_active)
    * [stop\_all](#apps.base_app.BaseApp.stop_all)
    * [delayed\_stop\_all](#apps.base_app.BaseApp.delayed_stop_all)
    * [restart\_all](#apps.base_app.BaseApp.restart_all)
    * [delayed\_restart\_all](#apps.base_app.BaseApp.delayed_restart_all)
    * [start\_all](#apps.base_app.BaseApp.start_all)
    * [delayed\_update](#apps.base_app.BaseApp.delayed_update)
    * [get\_services](#apps.base_app.BaseApp.get_services)
    * [get\_service](#apps.base_app.BaseApp.get_service)
    * [check\_update\_available](#apps.base_app.BaseApp.check_update_available)
    * [update](#apps.base_app.BaseApp.update)
    * [post\_update](#apps.base_app.BaseApp.post_update)
    * [get\_next\_available\_port](#apps.base_app.BaseApp.get_next_available_port)
    * [send\_discord\_message](#apps.base_app.BaseApp.send_discord_message)
    * [get\_app\_directory](#apps.base_app.BaseApp.get_app_directory)
    * [get\_home\_directory](#apps.base_app.BaseApp.get_home_directory)
    * [create\_service](#apps.base_app.BaseApp.create_service)
    * [remove](#apps.base_app.BaseApp.remove)
    * [remove\_service](#apps.base_app.BaseApp.remove_service)
    * [detect\_services](#apps.base_app.BaseApp.detect_services)
    * [get\_app\_uid](#apps.base_app.BaseApp.get_app_uid)
    * [get\_app\_gid](#apps.base_app.BaseApp.get_app_gid)
    * [first\_run](#apps.base_app.BaseApp.first_run)
    * [ensure\_file\_ownership](#apps.base_app.BaseApp.ensure_file_ownership)
    * [ensure\_file\_parent\_exists](#apps.base_app.BaseApp.ensure_file_parent_exists)
    * [makedirs](#apps.base_app.BaseApp.makedirs)
* [config](#config)
* [config.json\_config](#config.json_config)
  * [JSONConfig](#config.json_config.JSONConfig)
    * [get\_value](#config.json_config.JSONConfig.get_value)
    * [set\_value](#config.json_config.JSONConfig.set_value)
    * [has\_value](#config.json_config.JSONConfig.has_value)
    * [exists](#config.json_config.JSONConfig.exists)
    * [load](#config.json_config.JSONConfig.load)
    * [save](#config.json_config.JSONConfig.save)
* [config.ini\_config](#config.ini_config)
  * [INIConfig](#config.ini_config.INIConfig)
    * [get\_value](#config.ini_config.INIConfig.get_value)
    * [set\_value](#config.ini_config.INIConfig.set_value)
    * [has\_value](#config.ini_config.INIConfig.has_value)
    * [exists](#config.ini_config.INIConfig.exists)
    * [load](#config.ini_config.INIConfig.load)
    * [save](#config.ini_config.INIConfig.save)
* [config.unreal\_config](#config.unreal_config)
  * [UnrealConfig](#config.unreal_config.UnrealConfig)
    * [get\_value](#config.unreal_config.UnrealConfig.get_value)
    * [set\_value](#config.unreal_config.UnrealConfig.set_value)
    * [has\_value](#config.unreal_config.UnrealConfig.has_value)
    * [exists](#config.unreal_config.UnrealConfig.exists)
    * [load](#config.unreal_config.UnrealConfig.load)
    * [fetch](#config.unreal_config.UnrealConfig.fetch)
    * [save](#config.unreal_config.UnrealConfig.save)
* [config.properties\_config](#config.properties_config)
  * [PropertiesConfig](#config.properties_config.PropertiesConfig)
    * [get\_value](#config.properties_config.PropertiesConfig.get_value)
    * [set\_value](#config.properties_config.PropertiesConfig.set_value)
    * [has\_value](#config.properties_config.PropertiesConfig.has_value)
    * [exists](#config.properties_config.PropertiesConfig.exists)
    * [load](#config.properties_config.PropertiesConfig.load)
    * [save](#config.properties_config.PropertiesConfig.save)
* [config.cli\_config](#config.cli_config)
  * [CLIConfig](#config.cli_config.CLIConfig)
    * [get\_value](#config.cli_config.CLIConfig.get_value)
    * [set\_value](#config.cli_config.CLIConfig.set_value)
    * [has\_value](#config.cli_config.CLIConfig.has_value)
    * [exists](#config.cli_config.CLIConfig.exists)
    * [load](#config.cli_config.CLIConfig.load)
* [config.base\_config](#config.base_config)
  * [BaseConfig](#config.base_config.BaseConfig)
    * [add\_option](#config.base_config.BaseConfig.add_option)
    * [from\_system\_type](#config.base_config.BaseConfig.from_system_type)
    * [get\_value](#config.base_config.BaseConfig.get_value)
    * [set\_value](#config.base_config.BaseConfig.set_value)
    * [has\_value](#config.base_config.BaseConfig.has_value)
    * [get\_default](#config.base_config.BaseConfig.get_default)
    * [get\_type](#config.base_config.BaseConfig.get_type)
    * [get\_help](#config.base_config.BaseConfig.get_help)
    * [get\_options](#config.base_config.BaseConfig.get_options)
    * [exists](#config.base_config.BaseConfig.exists)
    * [load](#config.base_config.BaseConfig.load)
    * [save](#config.base_config.BaseConfig.save)
* [config.config\_key](#config.config_key)
  * [ConfigKey](#config.config_key.ConfigKey)
    * [from\_dict](#config.config_key.ConfigKey.from_dict)
    * [to\_system\_type](#config.config_key.ConfigKey.to_system_type)

## BaseMod Objects

```python
class BaseMod()
```

#### to\_dict

```python
def to_dict() -> dict
```

Returns a dict representation of the mod.

#### from\_dict

```python
@classmethod
def from_dict(cls, data: dict) -> 'BaseMod'
```

Populate an object from a flat dictionary, (ie; that of generated from JSON)

**Arguments**:

- `data`: 

#### \_\_str\_\_

```python
def __str__()
```

Returns a pretty string representation for pprint and print().

#### \_\_eq\_\_

```python
def __eq__(other)
```

Compare this mod against another and check if they are the same

**Arguments**:

- `other`: 

#### is\_same

```python
def is_same(other_mod: 'BaseMod') -> bool
```

Check if this mod is the same base mod as another, ignoring the version

This is suitable in installation checks to see if the mod should be updated or installed.

**Arguments**:

- `other_mod`: 

#### calculate\_files

```python
def calculate_files()
```

Calculate the files in this mod that are to be installed.


#### register

```python
def register()
```

Register a mod by adding it to the registration file.

Use a comparison key to ensure that the mod is only registered once.
This key should be one of the properties under BaseMod which can be used to uniquely identify the mod.


#### download

```python
def download() -> bool
```

Download this mod to the Packages cache

Requires source and package to be set


#### find\_mods

```python
@classmethod
def find_mods(cls, source: 'BaseService', mod_lookup: str) -> list['BaseMod']
```

Search for a mod manually added within Packages/

**Arguments**:

- `source`: Source game service to use for reference
- `mod_lookup`: Query text to lookup

#### get\_mod

```python
@classmethod
def get_mod(cls, source: 'BaseService', provider: str | None,
            mod_id: str | int) -> 'BaseMod | None'
```

Get a specific mod by ID, this only searches through manually-installed mods.

**Arguments**:

- `source`: Source game service to use for reference
- `provider`: Mod provider, e.g. 'curseforge'
- `mod_id`: Mod ID

#### get\_registered\_mods

```python
@classmethod
def get_registered_mods(cls) -> list['BaseMod']
```

Get all registered mods, eg all mods which are present in the registration file


#### save\_registered\_mods

```python
@classmethod
def save_registered_mods(cls, mods: list['BaseMod'])
```

Save the list of registered mods to the registration file

**Arguments**:

- `mods`: 

## WarlockNexusMod Objects

```python
class WarlockNexusMod(BaseMod)
```

#### find\_mods

```python
@classmethod
def find_mods(cls, source: 'BaseService',
              mod_lookup: str) -> list['WarlockNexusMod']
```

Search for a mod via Warlock.Nexus, must be a sponsor to use this.

**Arguments**:

- `source`: Source game service to use for reference
- `mod_lookup`: Query text to lookup

#### get\_mod

```python
@classmethod
def get_mod(cls, source: 'BaseService', provider: str | None,
            mod_id: str | int) -> 'WarlockNexusMod | None'
```

Get a specific mod by ID, must be a sponsor to use this.

**Arguments**:

- `source`: Source game service to use for reference
- `provider`: Mod provider, e.g. 'curseforge'
- `mod_id`: Mod ID

#### get\_meta

```python
def get_meta() -> dict
```

Get the meta information for this application

This relates to the information of the _management script_, not of the game.


#### parse\_version

```python
def parse_version(version_string: str) -> Version
```

Parse a version string into a Version object.

Supports standard semantic versioning (e.g., "1.2.3") and pre-release versions
(e.g., "1.0.0a1", "2.0.0rc1").

**Arguments**:

- `version_string`: The version string to parse

**Raises**:

- `ValueError`: If the version string is invalid

**Returns**:

A Version object

#### compare\_versions

```python
def compare_versions(version1: str | Version, version2: str | Version) -> int
```

Compare two versions.

**Arguments**:

- `version1`: First version as string or Version object
- `version2`: Second version as string or Version object

**Returns**:

-1 if version1 < version2, 0 if equal, 1 if version1 > version2

#### is\_version\_newer

```python
def is_version_newer(current: str | Version, candidate: str | Version) -> bool
```

Check if a candidate version is newer than the current version.

**Arguments**:

- `current`: The current version
- `candidate`: The candidate version to check

**Returns**:

True if candidate is newer than current

#### is\_version\_older

```python
def is_version_older(current: str | Version, candidate: str | Version) -> bool
```

Check if a candidate version is older than the current version.

**Arguments**:

- `current`: The current version
- `candidate`: The candidate version to check

**Returns**:

True if candidate is older than current

#### is\_version\_equal

```python
def is_version_equal(version1: str | Version, version2: str | Version) -> bool
```

Check if two versions are equal.

**Arguments**:

- `version1`: The first version
- `version2`: The second version

**Returns**:

True if versions are equal

#### get\_major\_version

```python
def get_major_version(version: str | Version) -> int
```

Extract the major version number from a version string.

**Arguments**:

- `version`: The version string or Version object

**Returns**:

The major version number

#### get\_minor\_version

```python
def get_minor_version(version: str | Version) -> int
```

Extract the minor version number from a version string.

**Arguments**:

- `version`: The version string or Version object

**Returns**:

The minor version number

#### get\_patch\_version

```python
def get_patch_version(version: str | Version) -> int
```

Extract the patch version number from a version string.

**Arguments**:

- `version`: The version string or Version object

**Returns**:

The patch version number

#### is\_prerelease

```python
def is_prerelease(version: str | Version) -> bool
```

Check if a version is a pre-release (alpha, beta, rc, etc).

**Arguments**:

- `version`: The version string or Version object

**Returns**:

True if the version is a pre-release

#### is\_postrelease

```python
def is_postrelease(version: str | Version) -> bool
```

Check if a version is a post-release.

**Arguments**:

- `version`: The version string or Version object

**Returns**:

True if the version is a post-release

#### is\_devrelease

```python
def is_devrelease(version: str | Version) -> bool
```

Check if a version is a development release.

**Arguments**:

- `version`: The version string or Version object

**Returns**:

True if the version is a development release

#### extract\_version\_from\_string

```python
def extract_version_from_string(text: str) -> str | None
```

Extract a version string from arbitrary text using regex pattern matching.

Matches patterns like "v1.2.3", "1.2.3", "version 1.2.3", etc.

**Arguments**:

- `text`: The text to search

**Returns**:

The extracted version string, or None if no version is found

#### normalize\_version

```python
def normalize_version(version: str) -> str
```

Normalize a version string to standard semantic versioning format.

Converts various formats to a consistent Version object representation.

**Arguments**:

- `version`: The version string to normalize

**Returns**:

The normalized version string

#### get\_version\_distance

```python
def get_version_distance(version1: str | Version,
                         version2: str | Version) -> tuple[int, int, int]
```

Get the distance between two versions in terms of major, minor, and patch.

**Arguments**:

- `version1`: The first version
- `version2`: The second version

**Returns**:

A tuple of (major_diff, minor_diff, patch_diff) representing the distance

#### is\_version\_compatible

```python
def is_version_compatible(
        current: str | Version,
        minimum_required: str | Version,
        maximum_required: str | Version | None = None) -> bool
```

Check if a current version is compatible with required version constraints.

Supports checking minimum required version and optionally maximum allowed version.

**Arguments**:

- `current`: The current version
- `minimum_required`: The minimum required version
- `maximum_required`: The maximum allowed version (optional, None for no upper bound)

**Returns**:

True if current version is compatible

#### menu\_public\_auth

```python
def menu_public_auth(nexus: Nexus)
```

Set the auth token for managing the public profile and managing hosts


## CmdFakeResponse Objects

```python
class CmdFakeResponse()
```

Fake response object to mimic subprocess.CompletedProcess for error handling when the command is not found.

## Cmd Objects

```python
class Cmd()
```

Simple subprocess wrapper to provide convenience methods for common interactions.

#### \_\_init\_\_

```python
def __init__(cmd: list)
```

Initialize a new command wrapper with the given command list.

**Arguments**:

- `cmd`: 

#### sudo

```python
def sudo(runas: str | int)
```

Run this command as another user using sudo.

If runas is a string, it will be treated as a username.
If runas is an int, it will be treated as a group ID.

If the requested user is the same as the current script runner, no sudo prefix will be added.

**Arguments**:

- `runas`: 

#### use\_stdout

```python
def use_stdout()
```

Set this command to use stdout for output instead of stderr.


#### use\_stderr

```python
def use_stderr()
```

Set this command to use stderr for output instead of stdout.


#### stream\_output

```python
def stream_output()
```

Set this command to stream to stdout/stderr directly.  Useful for long-running commands.


#### is\_cacheable

```python
def is_cacheable(expires: int = 3600)
```

Set this command as cacheable for N seconds.

**Arguments**:

- `expires`: 

#### is\_memory\_cacheable

```python
def is_memory_cacheable(expires: int = 2)
```

Set this command as cacheable in memory for N seconds.

**Arguments**:

- `expires`: 

#### exists

```python
@property
def exists() -> bool
```

Check if this binary exists


#### text

```python
@property
def text() -> str
```

Get the output of the command as raw text


#### lines

```python
@property
def lines() -> list
```

Get the output of the command as lines of text (as a list)


#### json

```python
@property
def json()
```

Get the output of the command decoded as JSON


#### success

```python
@property
def success() -> bool
```

Check if the command executed successfully (return code 0)


#### exit\_status

```python
@property
def exit_status() -> int
```

Get the return code of the command execution


#### run

```python
def run()
```

Run the command and capture the result. Caches the result so subsequent calls don't re-run the command.


#### extend

```python
def extend(args: list)
```

Extend the command with additional arguments.

**Arguments**:

- `args`: 

#### append

```python
def append(arg: str)
```

Append a single argument to the command.

**Arguments**:

- `arg`: 

## BackgroundCmd Objects

```python
class BackgroundCmd(Cmd)
```

Convenience wrapper for running commands in the background (with nohup).

#### run

```python
def run()
```

Run the command in the background using nohup. Caches the result so subsequent calls don't re-run the command.


#### get\_app\_directory

```python
def get_app_directory() -> str
```

Get the base directory for this game installation.

This directory usually will contain manage.py, AppFiles, Backups, and other related files.


#### get\_home\_directory

```python
def get_home_directory() -> str
```

Get the home directory of the user running this application


#### get\_app\_uid

```python
def get_app_uid() -> int
```

Get the user ID that should own the game files, based on the ownership of the executable directory


#### get\_app\_gid

```python
def get_app_gid() -> int
```

Get the group ID that should own the game files, based on the ownership of the executable directory


#### ensure\_file\_ownership

```python
def ensure_file_ownership(file: str)
```

Try to set the ownership of the given file to match the ownership of the game installation directory.

**Arguments**:

- `file`: 

#### ensure\_file\_parent\_exists

```python
def ensure_file_parent_exists(file: str)
```

A replacement of os.makedirs, but also sets permissions as it creates the directories.

This variation expects a child file to be requested.
It will create the parent directory if it does not exist, but will not touch the actual file itself.

**Arguments**:

- `file`: 

#### makedirs

```python
def makedirs(target_dir: str)
```

A replacement of os.makedirs, but also sets permissions as it creates the directories.

**Arguments**:

- `target_dir`: 

#### get\_wan\_ip

```python
def get_wan_ip() -> Union[str, None]
```

Get the external IP address of this server

**Returns**:

str: The external IP address as a string, or None if it cannot be determined

#### print\_header

```python
def print_header(title: str,
                 width: int = 80,
                 clear: bool = False,
                 subtitle: str = '') -> None
```

Prints a formatted header with a title and optional subtitle.

**Arguments**:

- `title` _str_ - The main title to display.
- `width` _int, optional_ - The total width of the header. Defaults to 80.
- `clear` _bool, optional_ - Whether to clear the console before printing. Defaults to False.

#### get\_terminal\_width

```python
def get_terminal_width(default: int = 80) -> int
```

Returns the width of the terminal window in characters.
Falls back to `default` if the size cannot be determined.

#### prompt\_long\_text

```python
def prompt_long_text(
        prompt: str = 'Enter the text in your editor and save/exit when done',
        default: str = '',
        suffix: str = '.txt') -> str
```

Prompt the user to edit a string in their preferred editor.

This is generally useful for editing long text that does not fit in a simple editor line.

**Arguments**:

- `prompt`: 
- `default`: 
- `suffix`: 

**Returns**:

str: The text input provided by the user.

#### prompt\_text

```python
def prompt_text(prompt: str = 'Enter text: ',
                default: str = '',
                prefill: bool = False) -> str
```

Prompt the user to enter text input and return the entered string.

**Arguments**:

- `prompt` _str_ - The prompt message to display to the user.
- `default` _str, optional_ - The default text to use if the user provides no input. Defaults to ''.
- `prefill` _bool, optional_ - If True, prefill the input with the default text. Defaults to False.

**Returns**:

- `str` - The text input provided by the user.

#### prompt\_yn

```python
def prompt_yn(prompt: str = 'Yes or no?', default: str = 'y') -> bool
```

Prompt the user with a Yes/No question and return their response as a boolean.

**Arguments**:

- `prompt` _str_ - The question to present to the user.
- `default` _str, optional_ - The default answer if the user just presses Enter.
  Must be 'y' or 'n'. Defaults to 'y'.
  

**Returns**:

- `bool` - True if the user answered 'yes', False if 'no'.

#### prompt\_options

```python
def prompt_options(prompt: str = 'Enter the option number: ',
                   options: list = None,
                   default: str = '') -> str
```

Prompt the user with a list of options and return the selected option.

The full text value of the option is returned, not the index!

    :param prompt: The prompt to display for input.

**Arguments**:

- `options`: The list of options to choose from.
- `default`: The default value to return if the user presses Enter.

**Returns**:

The selected option as a string.

## Table Objects

```python
class Table()
```

Displays data in a table format

#### \_\_init\_\_

```python
def __init__(columns: Union[list, None] = None)
```

Initialize the table with the columns to display

**Arguments**:

- `columns`: 

#### render

```python
def render()
```

Render the table with the given list of rows


## Firewall Objects

```python
class Firewall()
```

Simple utility class for managing firewall rules on the system.

Supports UFW, Firewalld, and iptables.
Provides methods to check for enabled and available firewalls, as well as to allow and remove specific ports.

#### get\_enabled

```python
@classmethod
def get_enabled(cls) -> str | None
```

Returns the name of the enabled firewall on the system.
Checks for UFW, Firewalld, and iptables in that order.

**Returns**:

- `str` - The name of the enabled firewall ('ufw', 'firewalld', 'iptables') or None if none are enabled.

#### get\_available

```python
@classmethod
def get_available(cls) -> str | None
```

Returns the name of the available firewall on the system.
Checks for UFW, Firewalld, and iptables in that order.

**Returns**:

- `str` - The name of the available firewall ('ufw', 'firewalld', 'iptables') or None if none are available.

#### allow

```python
@classmethod
def allow(cls, port: int, protocol: str = 'tcp', comment: str = None) -> None
```

Allows a specific port through the system's firewall.
Supports UFW, Firewalld, and iptables.

**Arguments**:

- `port` _int_ - The port number to allow.
- `protocol` _str, optional_ - The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.
- `comment` _str, optional_ - An optional comment for the rule. Defaults to None.

#### remove

```python
@classmethod
def remove(cls, port: int, protocol: str = 'tcp') -> None
```

Removes a specific port from the system's firewall.
Supports UFW, Firewalld, and iptables.

**Arguments**:

- `port` _int_ - The port number to remove.
- `protocol` _str, optional_ - The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.

#### is\_global\_open

```python
@classmethod
def is_global_open(cls, port: int, protocol: str = 'tcp') -> bool
```

Checks if a specific port is open in the system's firewall.
Supports UFW, Firewalld, and iptables.

This checks if the source host is global and not a specific host.

**Arguments**:

- `port` _int_ - The port number to check.
- `protocol` _str, optional_ - The protocol to use ('tcp' or 'udp'). Defaults to 'tcp'.

#### get\_listening\_port

```python
def get_listening_port(port: int, protocol: str) -> dict | None
```

Get the psutil definition for the listening port, or None if it's not open

If found, it returns a dictionary with the following keys:

pid: The PID of the listening process
ip: The IP address of the listening process (usually either 0.0.0.0, ::, 127.0.0.1, or an IP address)
status: The status of the listening process (e.g., LISTEN, TIME_WAIT, etc.)

**Arguments**:

- `port`: Port number (1-65535)
- `protocol`: Protocol, either TCP or UDP

#### get\_ports

```python
def get_ports(protocol: str) -> set[int]
```

Get all listening ports for the given protocol

**Arguments**:

- `protocol`: Protocol, either TCP or UDP

#### download\_file

```python
def download_file(url: str, destination: str)
```

Download a file from a URL to a destination path.

**Arguments**:

- `game`: The game instance, used to set ownership of the downloaded file
- `url`: The URL to download from
- `destination`: The local file path to save the downloaded file to

#### download\_json

```python
def download_json(url: str) -> dict
```

Download JSON data from a URL and return it as a dictionary.

This method supports caching, so the result is cached to disk,
and subsequent calls pull from that cache for a time.

**Arguments**:

- `game`: The game instance, used to set ownership of the downloaded file
- `url`: The URL to download from

**Returns**:

The JSON data as a dictionary

#### get\_java\_paths

```python
def get_java_paths() -> list[str]
```

Get a list of all Java executable paths available on the system using alternatives.

**Returns**:

A list of paths to Java executables

#### find\_java\_version

```python
def find_java_version(version: int) -> str
```

Find the path to the Java executable for the given version.

Uses alternatives / update-alternatives to detect paths.

**Arguments**:

- `version`: The major Java version to find (e.g., 11, 17, 21)

**Raises**:

- `RuntimeError`: If no Java executable matching the version is found

**Returns**:

The path to the Java executable matching the requested version

## SocketService Objects

```python
class SocketService(BaseService, ABC)
```

#### create\_service

```python
def create_service()
```

Create the systemd service for this game, including the service file and environment file


#### cmd

```python
def cmd(cmd) -> None | str
```

Send a command to the game server via its Systemd socket

**Arguments**:

- `cmd`: 

#### write\_socket

```python
def write_socket(content)
```

Simple write to socket command

Skips any checks to allow for raw access to the socket,
only checks if the socket file exists.

**Arguments**:

- `content`: 

#### watch

```python
def watch(callback: Callable[[str], Optional[bool]],
          timeout: int = 10) -> bool
```

Watch the systemd journal output for this service and call a callback function for each line.

The callback function should accept a single string argument (the journal line) and return:
- True: Line matched, continue watching and extend timeout by 0.5 seconds
- False: Found what we need, stop immediately
- None/other: Line didn't match, keep watching

**Arguments**:

- `callback`: Function that receives journal lines and returns True/False
- `timeout`: Maximum time to watch in seconds (default: 10)

**Returns**:

True if callback signaled completion (False return), False if timeout occurred

#### is\_api\_enabled

```python
def is_api_enabled() -> bool
```

Check if API is enabled for this service


#### get\_systemd\_config

```python
def get_systemd_config() -> SystemdUnitParser
```

Get the systemd unit configuration for this service, if available


#### remove\_service

```python
def remove_service()
```

Remove the systemd service for this game, including the service file and environment file


## HTTPService Objects

```python
class HTTPService(BaseService)
```

#### cmd

```python
def cmd(cmd: str) -> None | str
```

Send a command to the game server via the API, if available

**Arguments**:

- `cmd`: 

**Returns**:

None if the API is not available, or the result of the command

#### is\_api\_enabled

```python
def is_api_enabled() -> bool
```

Check if HTTP API is enabled for this service


#### get\_api\_port

```python
def get_api_port() -> int
```

Get the HTTP API port from the service configuration


#### get\_api\_password

```python
def get_api_password() -> str
```

Get the API password from the service configuration


#### get\_api\_username

```python
def get_api_username() -> str
```

Get the API username from the service configuration


## BaseService Objects

```python
class BaseService(ABC)
```

Service definition and handler

#### \_\_init\_\_

```python
def __init__(service: str, game: BaseApp)
```

Initialize and load the service definition

**Arguments**:

- `service`: The name of the systemd service to manage
- `game`: The game app instance this service belongs to

#### load

```python
def load()
```

Load the configuration files


#### get\_options

```python
def get_options() -> list
```

Get a list of available configuration options for this service


#### get\_option\_value

```python
def get_option_value(option: str) -> str | int | bool
```

Get a configuration option from the service config

**Arguments**:

- `option`: 

#### get\_option\_default

```python
def get_option_default(option: str) -> str
```

Get the default value of a configuration option

**Arguments**:

- `option`: 

#### get\_option\_type

```python
def get_option_type(option: str) -> str
```

Get the type of configuration option from the service config

**Arguments**:

- `option`: 

#### get\_option\_help

```python
def get_option_help(option: str) -> str
```

Get the help text of a configuration option from the service config

**Arguments**:

- `option`: 

#### option\_value\_updated

```python
def option_value_updated(option: str, previous_value, new_value)
```

Handle any special actions needed when an option value is updated

**Arguments**:

- `option`: 
- `previous_value`: 
- `new_value`: 

#### get\_option\_group

```python
def get_option_group(option: str)
```

Get the display group for a configuration option

**Arguments**:

- `option`: 

#### set\_option

```python
def set_option(option: str, value: str | int | bool)
```

Set a configuration option in the service config

**Arguments**:

- `option`: 
- `value`: 

#### option\_has\_value

```python
def option_has_value(option: str) -> bool
```

Check if a configuration option has a value set in the service config

**Arguments**:

- `option`: 

#### get\_option\_options

```python
def get_option_options(option: str)
```

Get the list of possible options for a configuration option

**Arguments**:

- `option`: 

#### option\_ensure\_set

```python
def option_ensure_set(option: str)
```

Ensure that a configuration option has a value set, using the default if not

**Arguments**:

- `option`: 

#### get\_name

```python
def get_name() -> str
```

Get the display name of this service


#### get\_ip

```python
def get_ip() -> str
```

Get the IP to connect to, can also be a hostname if necessary.

By default it just returns the WAN IP of the server.


#### get\_port

```python
def get_port() -> int | None
```

Get the primary port of the service, or None if not applicable


#### get\_port\_protocol

```python
def get_port_protocol() -> str | None
```

Get if the primary port of this service is UDP or TCP.

(Most games use UDP, but override this to change it)


#### prompt\_option

```python
def prompt_option(option: str)
```

Prompt the user to set a configuration option for the service

**Arguments**:

- `option`: 

#### get\_player\_max

```python
def get_player_max() -> int | None
```

Get the maximum player count on the server, or None if the API is unavailable


#### get\_player\_count

```python
def get_player_count() -> int | None
```

Get the current player count on the server, or None if the API is unavailable


#### get\_players

```python
def get_players() -> list | None
```

Get a list of current players on the server, or None if the API is unavailable


#### get\_pid

```python
def get_pid() -> int
```

Get the PID of the running service, or 0 if not running


#### get\_process\_status

```python
def get_process_status() -> int
```

Get the exit status of the main process of the service, or 0 if running successfully


#### get\_game\_pid

```python
@abstractmethod
def get_game_pid() -> int
```

Get the primary game process PID of the actual game server, or 0 if not running


#### get\_memory\_usage

```python
def get_memory_usage() -> str
```

Get the formatted memory usage of the service, or N/A if not running

Returns "# GB" or "# MB" depending on the amount of memory used,
or "N/A" if the memory usage cannot be determined (service not running, etc)


#### get\_cpu\_usage

```python
def get_cpu_usage() -> str
```

Get the formatted CPU usage of the service, or N/A if not running

Returns "#%" of CPU used, or "N/A" if the CPU usage cannot be determined (service not running, etc)


#### get\_exec\_start\_status

```python
def get_exec_start_status() -> dict | None
```

Get the ExecStart status of the service

This includes:

* path - string: Path of the ExecStartPre command
* arguments - string: Arguments passed to the ExecStartPre command
* start_time - datetime: Time the ExecStartPre command started
* stop_time - datetime: Time the ExecStartPre command stopped
* pid - int: PID of the ExecStartPre command
* code - string: Exit code of the ExecStartPre command
* status - int: Exit status of the ExecStartPre command
* runtime - int: Runtime of the ExecStartPre command in seconds


#### get\_exec\_start\_pre\_status

```python
def get_exec_start_pre_status() -> dict | None
```

Get the ExecStart status of the service

This includes:

* path - string: Path of the ExecStartPre command
* arguments - string: Arguments passed to the ExecStartPre command
* start_time - datetime: Time the ExecStartPre command started
* stop_time - datetime: Time the ExecStartPre command stopped
* pid - int: PID of the ExecStartPre command
* code - string: Exit code of the ExecStartPre command
* status - int: Exit status of the ExecStartPre command
* runtime - int: Runtime of the ExecStartPre command in seconds


#### is\_enabled

```python
def is_enabled() -> bool
```

Check if this service is enabled in systemd


#### is\_running

```python
def is_running() -> bool
```

Check if this service is currently running


#### is\_starting

```python
def is_starting() -> bool
```

Check if this service is currently starting


#### is\_stopping

```python
def is_stopping() -> bool
```

Check if this service is currently stopping


#### is\_stopped

```python
def is_stopped() -> bool
```

Check if this service is currently stopped


#### is\_api\_enabled

```python
def is_api_enabled() -> bool
```

Check if an API is available for this service


#### is\_port\_open

```python
def is_port_open() -> bool
```

Check if all required ports for this game are open


#### enable

```python
def enable()
```

Enable this service in systemd


#### disable

```python
def disable()
```

Disable this service in systemd


#### print\_logs

```python
def print_logs(lines: int = 20)
```

Print the latest logs from this service

**Arguments**:

- `lines`: 

#### get\_logs

```python
def get_logs(lines: int = 20) -> str
```

Get the latest logs from this service

**Arguments**:

- `lines`: 

#### send\_message

```python
def send_message(message: str)
```

Send a message to all players via the game API

**Arguments**:

- `message`: 

#### save\_world

```python
def save_world()
```

Force a world save via the game API


#### get\_port\_definitions

```python
@abstractmethod
def get_port_definitions() -> list
```

Get a list of port definitions for this service

Each entry in the returned list should contain 3 items:

* Config name or integer of port (for non-definable ports)
* 'UDP' or 'TCP' to indicate protocol
* Short description of the port purpose
* Optional boolean to indicate if this is an optional port (ie: not checked at startup)

Example:

```python
return [
        ['Game Port', 'UDP', 'Primary game port for clients to connect to', False],
        [25565, 'TCP', 'RCON port, statically assigned and cannot be changed', True]
]
```


#### get\_ports

```python
def get_ports() -> list
```

Get the list of all ports used by this game, (at least that are registered)

and their status

Each port in the returned list is expected to contain the following properties:

* port - Port number
* protocol - UDP or TCP to indicate the port protocol
* description - Short description of the port function
* global - T/F if this port listens globally
* listening - T/F if this port is currently open (listening)
* owned - T/F if this port is owned by this process
* open - T/F if this port is currently open in the firewall to default
* option - Option name that controls this port setting, or None if static


#### start

```python
def start()
```

Start this service in systemd


#### pre\_stop

```python
def pre_stop() -> bool
```

Perform operations necessary for safely stopping a server

Called automatically via systemd


#### post\_start

```python
def post_start() -> bool
```

Perform the necessary operations for after a game has started


#### stop

```python
def stop()
```

Stop this service in systemd


#### delayed\_stop

```python
def delayed_stop()
```

Delayed stop procedure for this service


#### restart

```python
def restart()
```

Restart this service in systemd


#### delayed\_restart

```python
def delayed_restart()
```

Delayed restart procedure for this service


#### reload

```python
def reload()
```

Reload systemd unit files to pick up changes to service configurations.


#### check\_update\_available

```python
def check_update_available() -> bool
```

Check if there's an update available for this game


#### update

```python
def update() -> bool
```

Update the game server


#### delayed\_update

```python
def delayed_update()
```

Perform a delayed update of the game, giving players time to log off safely before restarting the server.

Provides a 1-hour warning with 5-minute notifications, then updates the game and restarts all services.
This is intended to be used when performing maintenance or updates that require downtime,
but you want to give players a chance to log off safely before the server goes down.


#### post\_update

```python
def post_update()
```

Perform any post-update actions needed for this game

Called immediately after an update is performed but before services are restarted.


#### cmd

```python
def cmd(cmd: str) -> None | str
```

Send a command to the game server via the API, if available

**Arguments**:

- `cmd`: 

**Returns**:

None if the API is not available, or the result of the command

#### get\_commands

```python
def get_commands() -> None | list[str]
```

Get a list of available commands for this service


#### get\_systemd\_config

```python
def get_systemd_config() -> SystemdUnitParser
```

Get the systemd unit configuration for this service, if available


#### get\_app\_directory

```python
def get_app_directory() -> str
```

Get the working directory for this game service, which is the directory that contains the game files and executable

If the game is registered as a multi-binary game, each service is contained within its own directory,
otherwise all instances share AppFiles.


#### get\_save\_directory

```python
def get_save_directory() -> str
```

Get the parent directory that contains the Save files for this game

By default this is just the app directory (AppFiles or AppFiles/{servicename}),
but this can be changed if the game saves files outside this directory.


#### get\_backup\_directory

```python
def get_backup_directory() -> str
```

Get the backup directory for this game service, which is the directory that contains backups of the game files

If the game is registered as a multi-binary game, each service is contained within its own directory,
otherwise all instances share Backups.


#### get\_environment

```python
def get_environment() -> dict
```

Get the environment variables for this service as a dictionary


#### get\_info

```python
def get_info() -> dict
```

Get a dictionary of information about this service for display in the TUI

This is used by Warlock to retrieve information about a given service.


#### build\_systemd\_config

```python
def build_systemd_config()
```

Build and save the systemd service file for this service

WILL OVERWRITE ANY EXISTING SERVICE FILE WITHOUT PROMPT, USE WITH CAUTION


#### create\_service

```python
def create_service()
```

Create the systemd service for this game, including the service file and environment file


#### remove\_service

```python
def remove_service()
```

Remove the systemd service for this game, including the service file and environment file


#### get\_executable

```python
@abstractmethod
def get_executable() -> str
```

Get the full executable for this game service


#### get\_save\_files

```python
def get_save_files() -> list | None
```

Get the list of supplemental files or directories for this game, or None if not applicable

This list of files **should not** be fully resolved, and will use `self.get_app_directory()` as the base path.
For example, to return `AppFiles/SaveData` and `AppFiles/Config`:

```python
return ['SaveData', 'Config']
```


#### backup

```python
def backup(max_backups: int = 0) -> bool
```

Perform a backup of the game configuration and save files

**Arguments**:

- `max_backups`: Maximum number of backups to keep (0 = unlimited)

#### prepare\_backup

```python
def prepare_backup() -> str
```

Prepare a backup directory for this game and return the file path


#### complete\_backup

```python
def complete_backup(max_backups: int = 0) -> str
```

Complete the backup process by creating the final archive and cleaning up temporary files


#### restore

```python
def restore(path: str) -> bool
```

Restore a backup from the given filename

**Arguments**:

- `path`: 

#### prepare\_restore

```python
def prepare_restore(filename) -> str | bool
```

Prepare to restore a backup by extracting it to a temporary location

**Arguments**:

- `filename`: 

#### complete\_restore

```python
def complete_restore()
```

Complete the restore process by cleaning up temporary files


#### wipe

```python
def wipe()
```

Wipe player data and reset the game back to default state


#### get\_enabled\_mods

```python
def get_enabled_mods() -> list['BaseMod']
```

Get all enabled mods that are locally available on this service


#### add\_mod

```python
def add_mod(mod: 'BaseMod', force: bool = False) -> bool
```

Install a mod

**Arguments**:

- `mod`: Mod to install
- `force`: Force the installation even if the mod is already installed

#### install\_mod\_dependencies

```python
def install_mod_dependencies(mod: 'BaseMod')
```

Install the dependencies for a given mod

**Arguments**:

- `mod`: 

#### remove\_mod

```python
def remove_mod(mod: 'BaseMod') -> bool
```

Remove a mod

Will completely uninstall the requested mod

**Arguments**:

- `mod`: 

#### remove\_mod\_files

```python
def remove_mod_files(mod: 'BaseMod')
```

Remove the files for a given mod

Will NOT completely remove the mod from the game configuration, so safe to call during reinstall/upgrade.

**Arguments**:

- `mod`: 

#### get\_mod

```python
def get_mod(provider: str, mod_id: str | int) -> 'BaseMod | None'
```

Get the locally enabled mod that matches the given provider and mod ID

**Arguments**:

- `provider`: 
- `mod_id`: 

#### check\_mod\_files\_installed

```python
def check_mod_files_installed(mod: 'BaseMod', mode: str = 'any') -> bool
```

Check if a given mod already has files installed in the game.

Useful for a pre-check before a mod is installed to know if it will overwrite an existing file.
If `mode` is set to 'any' (default behaviour), will return True if ANY file is present.
else if `mode` is set to 'all', will return True only if ALL files are present.

**Arguments**:

- `mod`: Mod to check
- `mode`: Set to "any" or "all" (defaults to any)

#### install\_mod\_files

```python
def install_mod_files(mod: 'BaseMod') -> bool
```

Install the files into this game

**Arguments**:

- `mod`: 

#### get\_version

```python
def get_version() -> str | None
```

Get the version of the game binary


#### get\_loader

```python
def get_loader() -> str | None
```

Get the loader used to launch the game


## RCONService Objects

```python
class RCONService(BaseService)
```

#### cmd

```python
def cmd(cmd) -> None | str
```

Execute a raw command with RCON and return the result

**Arguments**:

- `cmd`: 

**Returns**:

None if RCON not available, or the result of the command

#### get\_player\_count

```python
def get_player_count() -> int | None
```

Get the current player count on the server, or None if the API is unavailable


#### is\_api\_enabled

```python
def is_api_enabled() -> bool
```

Check if RCON is enabled for this service


#### get\_api\_port

```python
def get_api_port() -> int
```

Get the RCON port from the service configuration


#### get\_api\_password

```python
def get_api_password() -> str
```

Get the RCON password from the service configuration


#### steamcmd\_parse\_manifest

```python
def steamcmd_parse_manifest(manifest_content)
```

Parses a SteamCMD manifest file content and returns a dictionary

with the all the relevant information.

Example format of content to parse:

"2131400"
{
        "common"
        {
                "name"          "VEIN Dedicated Server"
                "type"          "Tool"
                "parent"                "1857950"
                "ReleaseState"          "released"
                "oslist"                "windows,linux"
                "osarch"                "64"
                "osextended"            ""
                "icon"          "7573f431d9ecd0e9dc21f4406f884b92152508fd"
                "clienticon"            "b5de75f7c5f84027200fdafe0483caaeb80f7dbe"
                "clienttga"             "6012ea81d68607ad0dfc5610e61f17101373c1fd"
                "freetodownload"                "1"
                "associations"
                {
                }
                "gameid"                "2131400"
        }
        "extended"
        {
                "gamedir"               ""
        }
        "config"
        {
                "installdir"            "VEIN Dedicated Server"
                "launch"
                {
                        "0"
                        {
                                "executable"            "VeinServer.exe"
                                "type"          "default"
                                "config"
                                {
                                        "oslist"                "windows"
                                }
                                "description_loc"
                                {
                                        "english"               "VEIN Dedicated Server"
                                }
                                "description"           "VEIN Dedicated Server"
                        }
                        "1"
                        {
                                "executable"            "VeinServer.sh"
                                "type"          "default"
                                "config"
                                {
                                        "oslist"                "linux"
                                }
                                "description_loc"
                                {
                                        "english"               "VEIN Dedicated Server"
                                }
                                "description"           "VEIN Dedicated Server"
                        }
                }
                "uselaunchcommandline"          "1"
        }
        "depots"
        {
                "228989"
                {
                        "config"
                        {
                                "oslist"                "windows"
                        }
                        "depotfromapp"          "228980"
                        "sharedinstall"         "1"
                }
                "228990"
                {
                        "config"
                        {
                                "oslist"                "windows"
                        }
                        "depotfromapp"          "228980"
                        "sharedinstall"         "1"
                }
                "2131401"
                {
                        "config"
                        {
                                "oslist"                "windows"
                        }
                        "manifests"
                        {
                                "public"
                                {
                                        "gid"           "3422721066391688500"
                                        "size"          "13373528354"
                                        "download"              "4719647568"
                                }
                                "experimental"
                                {
                                        "gid"           "5376672931011513884"
                                        "size"          "14053570688"
                                        "download"              "4881399680"
                                }
                        }
                }
                "2131402"
                {
                        "config"
                        {
                                "oslist"                "linux"
                        }
                        "manifests"
                        {
                                "public"
                                {
                                        "gid"           "4027172715479418364"
                                        "size"          "14134939630"
                                        "download"              "4869512928"
                                }
                                "experimental"
                                {
                                        "gid"           "643377871134354986"
                                        "size"          "14712396815"
                                        "download"              "4982816608"
                                }
                        }
                }
                "branches"
                {
                        "public"
                        {
                                "buildid"               "20727232"
                                "timeupdated"           "1762674215"
                        }
                        "experimental"
                        {
                                "buildid"               "20729593"
                                "description"           "Bleeding-edge updates"
                                "timeupdated"           "1762704776"
                        }
                }
                "privatebranches"               "1"
        }
}

**Arguments**:

- `manifest_content`: str, content of the SteamCMD manifest file

**Returns**:

dict, parsed manifest data

## SteamApp Objects

```python
class SteamApp(BaseApp, ABC)
```

Game application manager

#### get\_app\_details

```python
def get_app_details() -> dict | None
```

Get detailed information about a Steam app using steamcmd

Returns a dictionary with:

- common
        - name
        - type
        - parent
        - ReleaseState
        - oslist
        - osarch
        - osextended
        - icon
        - clienticon
        - clienttga
        - freetodownload
        - associations
        - gameid
- extended
        - gamedir
- config
        - installdir
        - launch
        - uselaunchcommandline
- depots

**Arguments**:

- `app_id`: 
- `steamcmd_path`: 

#### get\_steam\_branches

```python
def get_steam_branches() -> list[str]
```

Get the list of branches available for this game on SteamCMD


#### check\_update\_available

```python
def check_update_available() -> bool
```

Check if a SteamCMD update is available for this game


#### update

```python
def update()
```

Update the game server via SteamCMD


## ManualApp Objects

```python
class ManualApp(BaseApp, ABC)
```

Application installer for manual installation.

Generally these are apps which require manual downloads and do not support an app store such as Steam.

#### get\_latest\_version

```python
@abstractmethod
def get_latest_version() -> str | None
```

Get the latest version available of the app.


#### download\_file

```python
@deprecated('download_file() has moved to utils')
def download_file(url: str, destination: str)
```

Download a file from a URL to a destination path.

**Arguments**:

- `url`: The URL to download from
- `destination`: The local file path to save the downloaded file to

#### download\_json

```python
@deprecated('download_json() has moved to utils')
def download_json(url: str) -> dict
```

Download JSON data from a URL and return it as a dictionary.

This method supports caching, so the result is cached to disk,
and subsequent calls pull from that cache for a time.

**Arguments**:

- `url`: The URL to download from

**Returns**:

The JSON data as a dictionary

## BaseApp Objects

```python
class BaseApp(ABC)
```

Game application manager

#### load

```python
def load()
```

Load the configuration files


#### save

```python
def save()
```

Save the configuration files back to disk


#### get\_options

```python
def get_options() -> list
```

Get a list of available configuration options for this game


#### get\_option\_value

```python
def get_option_value(option: str) -> str | int | bool
```

Get a configuration option from the game config

**Arguments**:

- `option`: 

#### get\_option\_default

```python
def get_option_default(option: str) -> str
```

Get the default value of a configuration option

**Arguments**:

- `option`: 

#### get\_option\_type

```python
def get_option_type(option: str) -> str
```

Get the type of configuration option from the game config

**Arguments**:

- `option`: 

#### get\_option\_help

```python
def get_option_help(option: str) -> str
```

Get the help text of a configuration option from the game config

**Arguments**:

- `option`: 

#### option\_value\_updated

```python
def option_value_updated(option: str, previous_value, new_value)
```

Handle any special actions needed when an option value is updated

**Arguments**:

- `option`: 
- `previous_value`: 
- `new_value`: 

#### set\_option

```python
def set_option(option: str, value: str | int | bool)
```

Set a configuration option in the game config

**Arguments**:

- `option`: 
- `value`: 

#### get\_option\_options

```python
def get_option_options(option: str)
```

Get the list of possible options for a configuration option

**Arguments**:

- `option`: 

#### get\_option\_group

```python
def get_option_group(option: str)
```

Get the display group for a configuration option

**Arguments**:

- `option`: 

#### prompt\_option

```python
def prompt_option(option: str)
```

Prompt the user to set a configuration option for the game

**Arguments**:

- `option`: 

#### is\_active

```python
def is_active() -> bool
```

Check if any service instance is currently running or starting


#### stop\_all

```python
def stop_all()
```

Stop all services with a 5-minute warning to players.


#### delayed\_stop\_all

```python
def delayed_stop_all()
```

Perform a delayed stop of all services, giving players time to log off safely before stopping the server.

Provides a 1-hour warning with 5-minute notifications, then stops all services.
This is intended to be used when performing maintenance or updates that require downtime,
but you want to give players a chance to log off safely before the server goes down.


#### restart\_all

```python
def restart_all()
```

Restart all services with a 5-minute warning to players.


#### delayed\_restart\_all

```python
def delayed_restart_all()
```

Perform a delayed restart of all services, giving players time to log off safely before restarting the server.

Provides a 1-hour warning with 5-minute notifications, then restarts all services.
This is intended to be used when performing maintenance or updates that require downtime,
but you want to give players a chance to log off safely before the server goes down.


#### start\_all

```python
def start_all()
```

Start all services that are enabled for auto-start.


#### delayed\_update

```python
def delayed_update()
```

Perform a delayed update of the game, giving players time to log off safely before restarting the server.

Provides a 1-hour warning with 5-minute notifications, then updates the game and restarts all services.
This is intended to be used when performing maintenance or updates that require downtime,
but you want to give players a chance to log off safely before the server goes down.


#### get\_services

```python
def get_services() -> list['BaseService']
```

Get a dictionary of available services (instances) for this game


#### get\_service

```python
def get_service(service_name: str) -> Optional['BaseService']
```

Get a specific service instance by name

**Arguments**:

- `service_name`: 

**Returns**:

BaseService instance or None if not found

#### check\_update\_available

```python
def check_update_available() -> bool
```

Check if there's an update available for this game


#### update

```python
def update() -> bool
```

Update the game server


#### post\_update

```python
def post_update()
```

Perform any post-update actions needed for this game

Called immediately after an update is performed but before services are restarted.


#### get\_next\_available\_port

```python
def get_next_available_port(service, port: int, protocol: str) -> int
```

Search through all ports used by all services under this game and find the next available one.

**Arguments**:

- `service`: The service instance that started the lookup, (its ports will be checked too)
- `port`: 
- `protocol`: 

#### send\_discord\_message

```python
def send_discord_message(message: str)
```

Send a message to the configured Discord webhook

**Arguments**:

- `message`: 

#### get\_app\_directory

```python
@deprecated("Please use get_app_directory() from utils instead.")
def get_app_directory() -> str
```

Get the base directory for this game installation.

This directory usually will contain manage.py, AppFiles, Backups, and other related files.


#### get\_home\_directory

```python
@deprecated("Please use get_home_directory() from utils instead")
def get_home_directory() -> str
```

Get the home directory of the user running this application


#### create\_service

```python
def create_service(service_name: str) -> 'BaseService'
```

Create a new service instance for this game with the given name

**Arguments**:

- `service_name`: 

#### remove

```python
def remove()
```

Remove this game and all instances under it


#### remove\_service

```python
def remove_service(service_name: str)
```

Remove a service instance for this game with the given name

**Arguments**:

- `service_name`: 

#### detect\_services

```python
def detect_services() -> list
```

Try to detect available services for this game.


#### get\_app\_uid

```python
@deprecated("Please use get_app_uid() from utils instead")
def get_app_uid() -> int
```

Get the user ID that should own the game files, based on the ownership of the executable directory


#### get\_app\_gid

```python
@deprecated("Please use get_app_gid() from utils instead")
def get_app_gid() -> int
```

Get the group ID that should own the game files, based on the ownership of the executable directory


#### first\_run

```python
def first_run() -> bool
```

Perform any first-run configuration needed for this game


#### ensure\_file\_ownership

```python
@deprecated("Please use ensure_file_ownership() from utils instead")
def ensure_file_ownership(file: str)
```

Try to set the ownership of the given file to match the ownership of the game installation directory.

**Arguments**:

- `file`: 

#### ensure\_file\_parent\_exists

```python
@deprecated("Please use ensure_file_parent_exists() from utils instead")
def ensure_file_parent_exists(file: str)
```

A replacement of os.makedirs, but also sets permissions as it creates the directories.

This variation expects a child file to be requested.
It will create the parent directory if it does not exist, but will not touch the actual file itself.

**Arguments**:

- `file`: 

#### makedirs

```python
@deprecated("Please use makedirs() from utils instead")
def makedirs(target_dir: str)
```

A replacement of os.makedirs, but also sets permissions as it creates the directories.

**Arguments**:

- `target_dir`: 

## JSONConfig Objects

```python
class JSONConfig(BaseConfig)
```

#### get\_value

```python
def get_value(name: str) -> Union[str, int, bool]
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load()
```

Load the configuration file from disk


#### save

```python
def save()
```

Save the configuration file back to disk


## INIConfig Objects

```python
class INIConfig(BaseConfig)
```

#### get\_value

```python
def get_value(name: str) -> Union[str, int, bool]
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load()
```

Load the configuration file from disk


#### save

```python
def save()
```

Save the configuration file back to disk


## UnrealConfig Objects

```python
class UnrealConfig(BaseConfig)
```

#### get\_value

```python
def get_value(name: str) -> Union[str, int, bool, list]
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool, list, float])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load()
```

Load the configuration file from disk


#### fetch

```python
def fetch() -> str
```

Render the configuration file to a string, used in saving back to the disk.


#### save

```python
def save()
```

Save the configuration file back to disk


## PropertiesConfig Objects

```python
class PropertiesConfig(BaseConfig)
```

Configuration handler for Java-style .properties files

#### get\_value

```python
def get_value(name: str) -> Union[str, int, bool]
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load()
```

Load the configuration file from disk


#### save

```python
def save()
```

Save the configuration file back to disk


## CLIConfig Objects

```python
class CLIConfig(BaseConfig)
```

#### get\_value

```python
def get_value(name: str) -> config_types
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load(arguments: str = '')
```

Load the configuration file from disk


## BaseConfig Objects

```python
class BaseConfig(ABC)
```

#### add\_option

```python
def add_option(option_dict: dict)
```

Add a configuration option to the available list

**Arguments**:

- `name`: 
- `section`: 
- `key`: 
- `default`: 
- `val_type`: 
- `help_text`: 

#### from\_system\_type

```python
def from_system_type(name: str, value: config_types) -> Union[str, list]
```

Convert a system type value to a string for storage

**Arguments**:

- `name`: 
- `value`: 

#### get\_value

```python
def get_value(name: str) -> Union[str, int, bool]
```

Get a configuration option from the config

**Arguments**:

- `name`: Name of the option

#### set\_value

```python
def set_value(name: str, value: Union[str, int, bool])
```

Set a configuration option in the config

**Arguments**:

- `name`: Name of the option
- `value`: Value to save

#### has\_value

```python
def has_value(name: str) -> bool
```

Check if a configuration option has been set

**Arguments**:

- `name`: Name of the option

#### get\_default

```python
def get_default(name: str) -> config_types
```

Get the default value of a configuration option

**Arguments**:

- `name`: 

#### get\_type

```python
def get_type(name: str) -> str
```

Get the type of a configuration option from the config

**Arguments**:

- `name`: 

#### get\_help

```python
def get_help(name: str) -> str
```

Get the help text of a configuration option from the config

**Arguments**:

- `name`: 

#### get\_options

```python
def get_options(name: str)
```

Get the list of valid options for a configuration option from the config

**Arguments**:

- `name`: 

#### exists

```python
def exists() -> bool
```

Check if the config file exists on disk


#### load

```python
def load(*args, **kwargs)
```

Load the configuration file from disk


#### save

```python
def save(*args, **kwargs)
```

Save the configuration file back to disk


## ConfigKey Objects

```python
class ConfigKey()
```

Configuration item for a single key.

Pulled automatically from the configuration file `configs.yaml`.

#### from\_dict

```python
@classmethod
def from_dict(cls, option)
```

Instantiate a new ConfigKey based off a YAML object definition.

**Arguments**:

- `option`: dict

**Returns**:

ConfigKey

#### to\_system\_type

```python
def to_system_type(value) -> config_types
```

Convert a string value to the appropriate system type based on this key's val_type

**Arguments**:

- `value`: 

