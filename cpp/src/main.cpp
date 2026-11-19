#include <main.hpp>

ENDSTONE_PLUGIN("bedrock_homes", "1.0.1-beta", Main)
{
    description = "A lightweight home points plugin for Endstone Minecraft Bedrock servers. ";

    command("home")
        .description("Teleport to home point")
        .usages("/home <home: str>", "/home <home: str> [player: str]")
        .permissions("white.endstone.bedrockhomes.commands.home");

    command("sethome")
        .description("Set home point")
        .usages("/sethome <home: str>", "/sethome <home: str> [player: str]")
        .permissions("white.endstone.bedrockhomes.commands.home");

    command("delhome")
        .description("Remove home point")
        .usages("/delhome <home: str>", "/delhome <home: str> [player: str]")
        .permissions("white.endstone.bedrockhomes.commands.home");
    
    command("homes")
        .description("Get list of home points")
        .usages("/homes", "/homes [player: str]")
        .permissions("white.endstone.bedrockhomes.commands.home");

    permission("white.endstone.bedrockhomes.commands.home")
        .description("Allow player to use a home, sethome, homes and delhome commands")
        .default_(endstone::PermissionDefault::True);

    permission("white.endstone.bedrockhomes.permissions.homemanage")
        .description("Allow player to manage homes")
        .default_(endstone::PermissionDefault::Operator);
}