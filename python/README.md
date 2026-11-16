# BedrockHomes — Python API

BedrockHomes is a home points plugin for [Endstone](https://github.com/EndstoneMC/endstone) Minecraft Bedrock servers. It provides a Python API that allows other plugins to create, retrieve, list, and delete player home points.

![Version](https://img.shields.io/badge/version-1.0.1-brightgreen)
![Endstone](https://img.shields.io/badge/endstone-%3E%3D0.11.0-blue)
![Storage](https://img.shields.io/badge/storage-SQLite-lightgrey)

> **Package:** `endstone-bedrock-homes` · **Version:** `1.0.1` · **Requires:** `endstone >= 0.11.0` · **Plugin name:** `bedrock_homes`

## Installation

BedrockHomes must be installed and enabled on the server. Other plugins can use its API by obtaining the plugin instance through Endstone's plugin manager.

For development environments, install the package from the repository:

```bash
pip install git+https://github.com/whittte169/BedrockHomes.git
```

Or clone the repository and install it in editable mode:

```bash
git clone https://github.com/whittte169/BedrockHomes.git
cd BedrockHomes
pip install -e .
```

## Getting the API

The plugin creates a `HomesManager` instance during `on_enable()` and exposes it through its `api` attribute. The plugin name is `bedrock_homes`.

```python
from endstone.plugin import Plugin
from endstone_bedrock_homes.api.manager import HomesManager

class MyPlugin(Plugin):
    api_version = "0.11"
    depend = ["bedrock_homes"]

    def on_enable(self) -> None:
        homes_plugin = self.server.plugin_manager.get_plugin("bedrock_homes")
        self.homes: HomesManager = homes_plugin.api
```

If BedrockHomes is optional for your plugin, use `soft_depend` and check that the plugin is available and enabled before accessing its API.

## API reference

All methods are provided by `endstone_bedrock_homes.api.manager.HomesManager`.

### Database methods

| Method | Returns | Description |
|---|---|---|
| `is_database_connected()` | `bool` | Returns whether the SQLite connection is available. |
| `database_open()` | `bool` | Opens the database, enables WAL mode, sets `synchronous=NORMAL`, and creates the `homes` table if it does not exist. |
| `database_close()` | `bool` | Closes the database connection. Returns `False` if the database is not connected or closing fails. |

### Home methods

| Method | Returns | Description |
|---|---|---|
| `create_home(name: str, home: str, position: str, dimension: str)` | `bool` | Inserts a home record. `position` should use the `x:y:z` format. |
| `select_home(name: str, home: str)` | `list[str \| None]` | Retrieves one matching record as `[name, home, position, dimension]`. Returns an empty list if no record is found or the query fails. |
| `get_homes_list(name: str)` | `list[tuple]` | Returns all home records belonging to the specified player name. Returns an empty list if none are found or the query fails. |
| `delete_home(name: str, home: str)` | `bool` | Deletes records matching the specified player name and home name. |

### Example

```python
# Create a home
self.homes.create_home(
    name="Steve",
    home="base",
    position="100:64:200",
    dimension="minecraft:overworld"
)

# Retrieve a specific home
home = self.homes.select_home("Steve", "base")
if home:
    player_name, home_name, position, dimension = home

# Get all homes belonging to a player
homes_list = self.homes.get_homes_list("Steve")
for player_name, home_name, position, dimension in homes_list:
    self.logger.info(f"{player_name}: {home_name} at {position} ({dimension})")

# Delete a home
self.homes.delete_home("Steve", "base")
```

## Commands

BedrockHomes registers these commands:

| Command | Description |
|---|---|
| `/home <home> [player]` | Teleport the command sender to a home. The optional player argument requires the home-management permission. |
| `/sethome <home> [player]` | Save a home at the sender's current location for the sender or, with permission, the specified player. |
| `/homes [player]` | List home points for the sender or, with permission, the specified player. |
| `/delhome <home> [player]` | Delete a home belonging to the sender or, with permission, the specified player. |

The optional target-player argument is checked against:

```text
white.endstone.bedrockhomes.permissions.homemanage
```

The regular command permission is:

```text
white.endstone.bedrockhomes.permissions.commands.home
```

## Database schema

The database file is `database.db` inside the plugin's data directory. The `homes` table contains:

| Column | Description |
|---|---|
| `name` | Player name associated with the home. |
| `home` | Name of the home point. |
| `position` | Coordinates stored as `x:y:z`. |
| `dimension` | Dimension identifier in which the home was created. |

SQLite is configured to use WAL journal mode and `synchronous=NORMAL`.

## Behaviour notes

- Home records are associated with player names, not player UUIDs.
- The stored position contains the `x`, `y`, and `z` coordinates; the dimension is stored separately.
- `select_home()` returns an empty list when the database is unavailable, the arguments are invalid, no matching row exists, or a query fails.
- `get_homes_list()` returns an empty list when no matching records are found or a query fails.
- `create_home()` uses `INSERT OR IGNORE`. The current table schema does not declare a uniqueness constraint for player/home pairs.
- `delete_home()` returns whether the SQL operation completed successfully; it does not check whether a row was actually deleted.
- Database operations are protected by a re-entrant lock.
- The plugin opens the database during `on_enable()` and closes it during `on_disable()`.

## Project layout

```text
src/endstone_bedrock_homes/
├── main.py          # Plugin entry point and command handlers
└── api/
    └── manager.py   # HomesManager and SQLite database operations
```

The Endstone entry point is declared in `pyproject.toml`:

```toml
[project.entry-points."endstone"]
bedrock_homes = "endstone_bedrock_homes.main:Main"
```

## Links

- Repository: https://github.com/whittte169/BedrockHomes
- Endstone: https://github.com/EndstoneMC/endstone
