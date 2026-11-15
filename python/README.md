# BedrockHomes

A lightweight home points system for [Endstone](https://github.com/EndstoneMC/endstone) (Minecraft Bedrock) servers.

BedrockHomes is a standalone plugin that allows players to save named home points and teleport back to them. Home data is stored locally in an SQLite database, including the player's name, home name, coordinates, and dimension.

![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![Endstone](https://img.shields.io/badge/endstone-%3E%3D0.11.0-blue)
![Storage](https://img.shields.io/badge/storage-SQLite-lightgrey)

> **Package:** `endstone-bedrock-homes` · **Version:** `1.0.0` · **Requires:** `endstone >= 0.11.0` · **Plugin name:** `bedrock_homes`
>
> **GitHub:** <https://github.com/whittte169/BedrockHomes>

---

## Table of contents

- [Features](#features)
- [Installation](#installation)
  - [For server owners](#for-server-owners)
  - [For developers](#for-developers)
- [Commands and permissions](#commands-and-permissions)
- [Storage](#storage)
- [API reference](#api-reference)
  - [Getting the API](#getting-the-api)
  - [HomesManager methods](#homesmanager-methods)
- [Behaviour notes](#behaviour-notes)
- [Project layout](#project-layout)
- [Building](#building)
- [Links](#links)

---

## Features

- Save named home points for players.
- Teleport players to a saved home.
- Remove saved home points.
- Store home data in a local SQLite database.
- Preserve the dimension as well as the player's coordinates.
- Use a thread-safe manager with a re-entrant lock around database operations.
- No external database service or additional configuration required.

---

## Installation

### For server owners

1. Download the latest `.whl` file from the [GitHub Releases](https://github.com/whittte169/BedrockHomes/releases) page.
2. Place the wheel file in your Endstone server's `plugins/` folder.
3. Restart the server.

BedrockHomes creates its data directory and SQLite database automatically when the plugin starts:

```text
plugins/bedrock_homes/
├── config.toml
└── database.db
```

The plugin creates an empty `config.toml` file if it does not already exist. The current implementation does not read settings from this file.

### For developers

Install the package directly from GitHub:

```bash
pip install git+https://github.com/whittte169/BedrockHomes.git
```

Or clone the repository and install it in editable mode:

```bash
git clone https://github.com/whittte169/BedrockHomes.git
cd BedrockHomes
pip install -e .
```

---

## Commands and permissions

BedrockHomes registers the following commands:

| Command | Description |
|---|---|
| `/home <home>` | Teleport to one of your saved home points. |
| `/sethome <home>` | Save a home point at your current position and dimension. |
| `/delhome <home>` | Remove one of your saved home points. |

Examples:

```text
/home base
/sethome base
/delhome base
```

All three commands are intended for in-game players. The plugin rejects command use from the console or other non-player command senders.

The command declarations use the permission node:

```text
white.endstone.bedrockhomes.permissions.home
```

The plugin also declares this permission in its permission metadata:

```text
white.endstone.bedrockhomes.commands.home
```

---

## Storage

BedrockHomes uses SQLite. Its database is stored at:

```text
plugins/bedrock_homes/database.db
```

The `homes` table contains these columns:

| Column | Description |
|---|---|
| `name` | Player name associated with the home. |
| `home` | Name of the saved home point. |
| `position` | Coordinates stored as `x:y:z`. |
| `dimension` | Name of the dimension in which the home was created. |

The database uses SQLite WAL journal mode and `synchronous=NORMAL`.

Home points are associated with player names. The current database schema does not define a unique constraint for player/home pairs.

---

## API reference

The manager is implemented in:

```python
from endstone_bedrock_homes.api.manager import HomesManager
```

The plugin creates a `HomesManager` instance during `on_enable()` and exposes it through `plugin.api`.

### Getting the API

Another plugin can retrieve the BedrockHomes plugin through Endstone's plugin manager:

```python
homes_plugin = self.server.plugin_manager.get_plugin("bedrock_homes")

if homes_plugin is not None and homes_plugin.is_enabled:
    self.homes = homes_plugin.api
```

If your plugin requires BedrockHomes, declare it as a dependency:

```python
class MyPlugin(Plugin):
    api_version = "0.11"
    depend = ["bedrock_homes"]
```

### HomesManager methods

| Method | Returns | Description |
|---|---|---|
| `is_database_connected()` | `bool` | Returns whether the SQLite connection is currently available. |
| `create_home(name: str, home: str, position: str, dimension: str)` | `bool` | Inserts a home record. `position` is expected in `x:y:z` format. |
| `select_home(name: str, home: str)` | `list[str \| None]` | Retrieves the matching record as `[name, home, position, dimension]`; returns an empty list when no record is found or the query fails. |
| `delete_home(name: str, home: str)` | `bool` | Deletes records matching the player name and home name. |
| `database_open()` | `bool` | Opens the database, enables SQLite WAL mode, and creates the `homes` table if necessary. |
| `database_close()` | `bool` | Closes the database connection. |

### Example

```python
homes_plugin = self.server.plugin_manager.get_plugin("bedrock_homes")
homes = homes_plugin.api

# Save a home point
homes.create_home(
    name="Steve",
    home="base",
    position="100:64:200",
    dimension="minecraft:overworld"
)

# Retrieve a home point
home = homes.select_home("Steve", "base")

if home:
    player_name, home_name, position, dimension = home

# Remove a home point
homes.delete_home("Steve", "base")
```

`HomesManager` is intended to be used while the BedrockHomes plugin is enabled and its database connection is open.

---

## Behaviour notes

- Home records are keyed by player name and home name.
- The saved position contains the player's `x`, `y`, and `z` coordinates.
- The dimension is stored separately and used when resolving the destination for `/home`.
- `/home` reports an error if the requested home record or its dimension cannot be found.
- `/sethome` records the player's current location and dimension.
- The current command implementation expects a home name for `/sethome` and `/delhome`, even though their usage strings show the argument in square brackets.
- `create_home()` uses `INSERT OR IGNORE`; the table currently has no uniqueness constraint that would make duplicate player/home pairs conflict.
- `delete_home()` reports whether the database operation succeeded, not whether a matching row was actually removed.
- The plugin closes its database connection during `on_disable()`.

---

## Project layout

```text
src/endstone_bedrock_homes/
├── main.py          # Plugin entry point and command handlers
└── api/
    └── manager.py   # HomesManager: home records and SQLite lifecycle
```

The plugin entry point is declared in `pyproject.toml`:

```toml
[project.entry-points."endstone"]
bedrock_homes = "endstone_bedrock_homes.main:Main"
```

---

## Building

Build a wheel from the repository root:

```bash
pip install build
python -m build --wheel
```

The resulting package will be available in the `dist/` directory.

---

## Links

- Repository: <https://github.com/whittte169/BedrockHomes>
- Releases: <https://github.com/whittte169/BedrockHomes/releases>
- Endstone: <https://github.com/EndstoneMC/endstone>
