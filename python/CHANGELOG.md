# Changelog

All notable changes to BedrockHomes are documented in this file.

## [1.0.1] - 2026-11-16

### Added
- Added the `/homes` command to display a player's saved home points.
- Added optional target-player arguments to `/home`, `/sethome`, `/homes`, and `/delhome`.
- Added the `homemanage` permission for managing and viewing another player's homes.
- Added `HomesManager.get_homes_list()` to retrieve all home points belonging to a player.

### Changed
- Updated command usage declarations to include the optional target-player argument.
- Expanded the plugin's command permission metadata to cover the home-management commands.

## [1.0.0]

### Added
- Initial release of BedrockHomes.
- Added commands for creating, teleporting to, and deleting home points.
- Added SQLite-based storage for player names, home names, coordinates, and dimensions.
- Added the `HomesManager` Python API.
