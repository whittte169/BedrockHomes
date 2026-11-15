import tomli_w
import os
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
            "usages": ["/home <home: str>"],
            "permissions": ["white.endstone.bedrockhomes.permissions.home"]
        },
        "sethome": {
            "description": "Set home point",
            "usages": ["/sethome [home: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.home"]
        },
        "delhome": {
            "description": "Remove home point",
            "usages": ["/delhome [home: str]"],
            "permissions": ["white.endstone.bedrockhomes.permissions.home"]
        }
    }
    permissions = {
        "white.endstone.bedrockhomes.commands.home": {
            "description": "Allow player to use a home, sethome, homes and delhome commands",
            "default": True
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
            home = self.api.select_home(sender.name, args[0])
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
            sender.send_message(f"You teleported to '{home[0]}'")
            return True
        if command.name == "sethome":
            if not isinstance(sender, Player):
                sender.send_error_message("Only players can use this command!")
                return False
            if args is None or len(args) < 1:
                sender.send_error_message(command.usages[0])
                return False
            location = sender.location
            dimension = sender.dimension.name
            position = f"{location.x}:{location.y}:{location.z}"
            if not self.api.create_home(sender.name, args[0], position, dimension):
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
            if not self.api.delete_home(sender.name, args[0]):
                sender.send_error_message("Error! Failed to remove home point!")
                return False
            sender.send_message(f"You removed '{args[0]}' home point")
            return True