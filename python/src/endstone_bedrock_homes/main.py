import os
import json
import re
import threading
import urllib.request
import urllib.error
from endstone.plugin import Plugin
from endstone import Player, ColorFormat
from endstone.command import Command, CommandSender
from endstone.level import Location
from endstone_bedrock_homes.api.manager import HomesManager

class Main(Plugin):
    api_version = "0.11"
    commands = {
        "home": {
            "description": "Teleport to home point",
            "usages": ["/home <home: str>", "/home <home: str> [player: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.commands.home"]
        },
        
        "sethome": {
            "description": "Set home point",
            "usages": ["/sethome <home: str>", "/sethome <home: str> [player: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.commands.home"]
        },
        "delhome": {
            "description": "Remove home point",
            "usages": ["/delhome <home: str>", "/delhome <home: str> [player: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.commands.home"]
        },
        "homes": {
            "description": "Get list of home points",
            "usages": ["/homes", "/homes [player: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.commands.home"]
        }
    }
    permissions = {
        "white.endstone.bedrockhomes.permissions.commands.home": {
            "description": "Allow player to use a home, sethome, homes and delhome commands",
            "default": True
        },
        "white.endstone.bedrockhomes.permissions.homemanage": {
            "description": "Allow player to manage homes",
            "default": "op"
        }
    }

    def on_enable(self) -> None:
        self.api = HomesManager(self)
        self.api.database_open()
        if not self.api.is_database_connected():
            self.logger.error("Database wasn't opened!")
            self.server.plugin_manager.disable_plugin(self)
            return
        self.register_events(self)
        data_folder = self.data_folder
        config = os.path.join(data_folder, "config.toml")
        if not os.path.exists(data_folder):
            os.makedirs(data_folder, exist_ok=True)
        if not os.path.exists(config):
            with open(config, "wb") as f:
                pass
        self.logger.info("BedrockHomes was successfully loaded!")
        self.logger.info(f"GitHub: {ColorFormat.GREEN}https://github.com/whittte169/BedrockHomes{ColorFormat.RESET}")
        threading.Thread(target=self._check_updates, daemon=True).start()

    def _check_updates(self) -> None:
        url = "https://github.com"
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5"
                }
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                html = response.read().decode("utf-8", errors="ignore")
            matches = re.findall(r"python-([\d.]+)-stable", html)
            if not matches:
                return
            current_version_str = getattr(self.description, "version", "0.0.0")
            current_version = tuple(int(x) for x in re.findall(r"\d+", current_version_str))
            latest_version = current_version
            latest_version_str = current_version_str
            for ver_str in set(matches):
                ver_tuple = tuple(int(x) for x in ver_str.split("."))
                if ver_tuple > latest_version:
                    latest_version = ver_tuple
                    latest_version_str = ver_str
            if latest_version > current_version:
                self.logger.info(
                    f"{ColorFormat.YELLOW}A new stable release of BedrockHomes is available: "
                    f"v{latest_version_str} (current: v{current_version_str}){ColorFormat.RESET}"
                )
                self.logger.info(
                    f"{ColorFormat.GREEN}Download: https://github.com{ColorFormat.RESET}"
                )
        except urllib.error.HTTPError as e:
            self.logger.warning(f"Failed to check for updates (HTTP {e.code}): {e.reason}")
        except urllib.error.URLError as e:
            self.logger.warning(f"Failed to check for updates (Network error): {e.reason}")
        except Exception as e:
            self.logger.warning(f"Failed to check for updates: {e}")

    def on_disable(self) -> None:
        if hasattr(self, "api") and self.api is not None:
            self.api.database_close()

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if not self.api.is_database_connected():
            sender.send_error_message("Homes database is unavailable!")
            return False
        if command.name == "home":
            if not isinstance(sender, Player):
                sender.send_error_message("Only players can use this command!")
                return False
            if args is None or len(args) < 1:
                sender.send_error_message(command.usages[0])
                return False
            target = None
            if len(args) > 1:
                if not sender.has_permission("white.endstone.bedrockhomes.permissions.homemanage"):
                    sender.send_error_message("You don't have any permission to use this command!")
                    return False
                target = args[1]
            home = self.api.select_home(target if target is not None else sender.name, args[0])
            if home is None or len(home) != 4:
                sender.send_error_message(f"Error! Home '{args[0]}' isn't found!")
                return False
            position = home[2].split(":")
            dimension_name = home[3]
            dimension = self.server.level.get_dimension(dimension_name)
            if dimension is None:
                sender.send_error_message(f"Error! Dimension '{dimension_name}' isn't found!")
                return False
            location = Location(dimension, float(position[0]), float(position[1]), float(position[2]))
            sender.teleport(location)
            sender.send_message(f"You teleported to '{home[1]}'")
            return True
        if command.name == "homes":
            target = None
            if args is not None and len(args) >= 1:
                if not sender.has_permission("white.endstone.bedrockhomes.permissions.homemanage"):
                    sender.send_error_message("You don't have any permission to use this command!")
                    return False
                target = args[0]
            homes = self.api.get_homes_list(target if target is not None else sender.name)
            if len(homes) < 1:
                sender.send_message("You don't have any home points!")
                return True
            home_names = []
            for [_name, home_name, _position, _dimension] in homes:
                home_names.append(home_name)
            sender.send_message(f"Home points: {', '.join(home_names)}")
            return True
        if command.name == "sethome":
            if not isinstance(sender, Player):
                sender.send_error_message("Only players can use this command!")
                return False
            if args is None or len(args) < 1:
                sender.send_error_message(command.usages[0])
                return False
            target = None
            if len(args) > 1:
                if not sender.has_permission("white.endstone.bedrockhomes.permissions.homemanage"):
                    sender.send_error_message("You don't have any permission to use this command!")
                    return False
                target = args[1]
            location = sender.location
            dimension = sender.dimension.name
            position = f"{location.x}:{location.y}:{location.z}"
            if not self.api.create_home(target if target is not None else sender.name, args[0], position, dimension):
                sender.send_error_message("Error! Failed to set home point!")
                return False
            sender.send_message(f"You created '{args[0]}' home point")
            return True
        if command.name == "delhome":
            if not isinstance(sender, Player):
                sender.send_error_message("Only players can use this command!")
                return False
            if args is None or len(args) < 1:
                sender.send_error_message(command.usages[0])
                return False
            target = None
            if len(args) > 1:
                if not sender.has_permission("white.endstone.bedrockhomes.permissions.homemanage"):
                    sender.send_error_message("You don't have any permission to use this command!")
                    return False
                target = args[1]
            if not self.api.delete_home(target if target is not None else sender.name, args[0]):
                sender.send_error_message("Error! Failed to remove home point!")
                return False
            sender.send_message(f"You removed '{args[0]}' home point")
            return True
        return False