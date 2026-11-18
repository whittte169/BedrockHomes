# BedrockHomes — C++ API

BedrockHomes is a home points plugin for [Endstone](https://github.com/EndstoneMC/endstone) Minecraft Bedrock servers. Written in C++20 and backed by SQLite, it provides commands for managing player home points as well as an internal `HomeManager` API for database operations.

![Version](https://img.shields.io/badge/version-1.0.0--beta-brightgreen)
![Endstone](https://img.shields.io/badge/endstone-%3E%3D0.11.0-blue)
![C++](https://img.shields.io/badge/C%2B%2B-20-00599C)
![Storage](https://img.shields.io/badge/storage-SQLite-lightgrey)

> **Target:** `BedrockHomes` · **Version:** `1.0.0-beta` · **Requires:** `endstone >= 0.11.0` · **Plugin name:** `bedrock_homes`

## Building from source

BedrockHomes uses CMake and automatically fetches the Endstone C++ SDK (`v0.11` by default) via `FetchContent`. SQLite3 and `sqlite_modern_cpp` are bundled directly inside `include/`.

### Prerequisites

- CMake `3.15` or higher
- A C++20-compatible compiler (GCC, Clang, or MSVC)
- Git (for fetching Endstone headers)

### Build instructions

```bash
git clone https://github.com/whittte169/BedrockHomes.git
cd BedrockHomes/cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

To target a different Endstone API version, pass `-DENDSTONE_API_VERSION=<version>` during configuration:

```bash
cmake -B build -DENDSTONE_API_VERSION=0.11
```

Copy the compiled shared library (`.dll` on Windows, Linux format `.so` isn't supporting now) from the `build/` directory into your server's `plugins/` folder.

## Using `HomeManager`

The plugin instantiates `HomeManager` inside `Main::onEnable()` via `std::unique_ptr<HomeManager> api` and passes the `endstone::Plugin` reference to initialize the database inside the plugin's data folder.

If you are extending BedrockHomes or embedding `manager.hpp` in a C++ plugin:

```cpp
#include <endstone/endstone.hpp>
#include <manager.hpp>
#include <memory>

class MyPlugin : public endstone::Plugin {
private:
    std::unique_ptr<HomeManager> homes;

public:
    void onEnable() override {
        homes = std::make_unique<HomeManager>(*this);
    }
};
```

> **Note:** In `Main` (`include/main.hpp`), the `api` member is currently `private` and not exposed via a public getter or Endstone service registration, so external plugins cannot access it at runtime without exposing a public accessor.

## API reference

All methods are provided by `HomeManager` in `include/manager.hpp`.

### Constructor

| Signature | Description |
|---|---|
| `explicit HomeManager(endstone::Plugin &plugin)` | Ensures the plugin data directory exists, opens `database.db`, configures `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL`, and creates the `homes` table if it does not exist. |

### Home methods

| Method | Returns | Description |
|---|---|---|
| `createHome(std::string name, std::string home, std::string position, std::string dimension)` | `void` | Inserts a home record using `INSERT OR IGNORE`. `position` uses the `x:y:z` format. |
| `selectHome(const std::string &name, const std::string &home)` | `std::vector<std::string>` | Retrieves one matching record as `{name, home, position, dimension}`. Returns an empty vector if no record is found or the query fails. |
| `getHomesList(const std::string &name)` | `std::vector<std::vector<std::string>>` | Returns all home records belonging to the specified player name. Returns an empty vector if none are found or the query fails. |
| `deleteHome(std::string name, std::string home)` | `void` | Deletes records matching the specified player name and home name. |

### Example

```cpp
// Create a home
homes->createHome(
    "Steve",
    "base",
    "100.000000:64.000000:200.000000",
    "minecraft:overworld"
);

// Retrieve a specific home
std::vector<std::string> home = homes->selectHome("Steve", "base");
if (home.size() == 4) {
    const std::string &playerName = home[0];
    const std::string &homeName   = home[1];
    const std::string &position   = home[2];
    const std::string &dimension  = home[3];
}

// Get all homes belonging to a player
auto homesList = homes->getHomesList("Steve");
for (const auto &entry : homesList) {
    getLogger().info("{}: {} at {} ({})", entry[0], entry[1], entry[2], entry[3]);
}

// Delete a home
homes->deleteHome("Steve", "base");
```

## Commands

BedrockHomes registers these commands in `src/main.cpp`:

| Command | Usage | Description |
|---|---|---|
| `/home` | `/home <home: str> [player: str]` | Teleport the sender to a home. The optional player argument requires the home-management permission. |
| `/sethome` | `/sethome <home: str> [player: str]` | Save a home at the sender's current location for the sender or, with permission, the specified player. |
| `/homes` | `/homes [player: str]` | List home points for the sender or, with permission, the specified player. |
| `/delhome` | `/delhome <home: str> [player: str]` | Delete a home belonging to the sender or, with permission, the specified player. |

The optional target-player argument is checked against:

```text
white.endstone.bedrockhomes.permissions.homemanage
```

The regular command permission (granted to all players by default) is:

```text
white.endstone.bedrockhomes.commands.home
```

## Database schema

The database file is `database.db` inside the plugin's data directory (`plugin.getDataFolder() / "database.db"`). The `homes` table contains:

| Column | Type | Description |
|---|---|---|
| `name` | `TEXT` | Player name associated with the home. |
| `home` | `TEXT` | Name of the home point. |
| `position` | `TEXT` | Coordinates stored as `x:y:z`. |
| `dimension` | `TEXT` | Dimension identifier in which the home was created. |

SQLite is configured to use WAL journal mode and `synchronous=NORMAL`.

## Behaviour notes

- Home records are associated with player names, not player UUIDs.
- Coordinates are serialized with `std::to_string` in `x:y:z` format and parsed back via `std::stof` when teleporting; the dimension name is stored separately.
- `selectHome()` returns an empty `std::vector<std::string>` when no matching row exists or a SQLite exception occurs.
- `getHomesList()` returns an empty `std::vector<std::vector<std::string>>` when no matching records are found or a query fails.
- `createHome()` uses `INSERT OR IGNORE`, though the current `homes` table schema does not declare a uniqueness constraint on `(name, home)`.
- If database initialization fails during `onEnable()`, the plugin logs the error and disables itself via `getServer().getPluginManager().disablePlugin(*this)`.
- The SQLite connection is managed via RAII inside `sqlite::database` and closed automatically when `HomeManager` is destroyed on plugin unload.

## Project layout

```text
cpp/
├── .clang-format               # C++20 LLVM-based code formatting rules
├── CMakeLists.txt              # CMake build configuration & Endstone FetchContent
├── include/
│   ├── main.hpp                # Plugin lifecycle (Main) and command handlers
│   ├── manager.hpp             # HomeManager and SQLite database operations
│   ├── version.hpp.in          # CMake version header template
│   ├── sqlite3.c               # Amalgamated SQLite3 source
│   ├── sqlite3.h               # SQLite3 C header
│   ├── sqlite_modern_cpp.h     # Header-only C++ wrapper for SQLite3
│   └── sqlite_modern_cpp/      # sqlite_modern_cpp internal headers
└── src/
    └── main.cpp                # ENDSTONE_PLUGIN definition, commands, and permissions
```

## Links

- Repository: https://github.com/whittte169/BedrockHomes
- Endstone: https://github.com/EndstoneMC/endstone