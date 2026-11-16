# BedrockHomes

BedrockHomes is a lightweight home points plugin for [Endstone](https://github.com/EndstoneMC/endstone) Minecraft Bedrock servers.

It allows players to save named locations and teleport back to them whenever they need. Each home stores the player's name, coordinates, and dimension in a local SQLite database. The plugin also provides commands for managing home points and a Python API for integration with other Endstone plugins.

![Version](https://img.shields.io/badge/version-1.0.1-brightgreen)
![Endstone](https://img.shields.io/badge/endstone-%3E%3D0.11.0-blue)
![Storage](https://img.shields.io/badge/storage-SQLite-lightgrey)

> **Package:** `endstone-bedrock-homes` · **Version:** `1.0.1` · **Requires:** `endstone >= 0.11.0` · **Plugin name:** `bedrock_homes`

## Features

- Create named home points.
- Teleport to saved home points.
- List your saved homes.
- Delete home points.
- Allow authorized players to manage another player's homes.
- Store home coordinates and dimensions in a local SQLite database.
- Provide a Python API through `HomesManager`.
- Use SQLite WAL mode and a thread-safe manager for database operations.

## Installation

1. Download the latest `.whl` package from the [Releases](#) page.
2. Place the downloaded file in your Endstone server's `plugins/` directory.
3. Restart the server.

BedrockHomes creates its data directory and SQLite database automatically:

```text
plugins/bedrock_homes/
└── database.db
```

## Commands

| Command | Description |
|---|---|
| `/sethome <home>` | Save a home at your current location. |
| `/home <home>` | Teleport to one of your saved homes. |
| `/homes` | List your saved home points. |
| `/delhome <home>` | Delete one of your saved homes. |

Players with the home-management permission can also specify a target player:

```text
/sethome <home> <player>
/home <home> <player>
/homes <player>
/delhome <home> <player>
```

## Permissions

| Permission | Description | Default |
|---|---|---|
| `white.endstone.bedrockhomes.permissions.commands.home` | Allows use of `/home`, `/sethome`, `/homes`, and `/delhome`. | Everyone |
| `white.endstone.bedrockhomes.permissions.homemanage` | Allows managing and viewing another player's homes through the commands. | Operators |

## Documentation
- [Python Documentation](https://github.com/whittte169/BedrockHomes/blob/main/python/README.md) — Python API documentation, `HomesManager` reference, and examples.

## Storage

Home data is stored in an SQLite database at:

```text
plugins/bedrock_homes/database.db
```

The `homes` table stores the player name, home name, position (`x:y:z`), and dimension.

## Requirements

- [Endstone](https://github.com/EndstoneMC/endstone) `>= 0.11.0`

## License

BedrockHomes is distributed under the terms of the [LICENSE](#) file.

## Links

- [GitHub Repository](#)
- [Releases](#)
- [Changelog](#)
