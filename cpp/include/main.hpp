
#pragma once
#include <endstone/endstone.hpp>
#include <string>
#include <sstream>
#include <array>
#include <vector>
#include <memory>
#include <exception>
#include <manager.hpp>

class Main : public endstone::Plugin {
private:
    std::unique_ptr<HomeManager> api;
public:
    void onEnable() override {
        try {
            api = std::make_unique<HomeManager>(*this);
            getLogger().info("BedrockHomes was successfully loaded!");
            getLogger().info("GitHub: " + std::string(endstone::ColorFormat::Green) + "https://github.com" + std::string(endstone::ColorFormat::Reset));
        } catch (const std::exception &e) {
            getLogger().error(std::string("Failed to load database! ") + e.what());
            getServer().getPluginManager().disablePlugin(*this);
        }
    }
    bool onCommand(endstone::CommandSender &sender, const endstone::Command &command, const std::vector<std::string> &args) override {
        if (!api) {
            sender.sendErrorMessage("Homes database is unavailable!");
            return false;
        }
        if (command.getName() == "home") {
            endstone::Player *player = sender.asPlayer();
            if (!player) {
                sender.sendErrorMessage("Only players can use this command!");
                return false;
            }
            if (args.empty()) {
                sender.sendErrorMessage(command.getUsages()[0]);
                return false;
            }
            std::string target = player->getName();
            if (args.size() > 1) {
                if (!sender.hasPermission("white.endstone.bedrockhomes.permissions.homemanage")) {
                    sender.sendErrorMessage("You don't have any permission to use this command!");
                    return false;
                }
                target = args[1];
            }
            std::vector<std::string> home = api->selectHome(target, args[0]);
            if (home.size() != 4) {
                sender.sendErrorMessage("Error! Home '" + args[0] + "' isn't found!");
                return false;
            }
            std::array<float, 3> coords{0.0f, 0.0f, 0.0f};
            std::istringstream iss(home[2]);
            std::string token;
            size_t index = 0;
            while (std::getline(iss, token, ':') && index < 3) {
                coords[index++] = std::stof(token);
            }
            endstone::Dimension *dimension = getServer().getLevel()->getDimension(home[3]);
            if (!dimension) {
                sender.sendErrorMessage("Error! Dimension '" + home[3] + "' isn't found!");
                return false;
            }
            endstone::Location location{
                *dimension,
                coords[0],
                coords[1],
                coords[2]
            };
            player->teleport(location);
            player->sendMessage("You teleported to '" + home[1] + "'");
            return true;
        }
        if (command.getName() == "homes") {
            std::string target = sender.getName();
            if (!args.empty()) {
                if (!sender.hasPermission("white.endstone.bedrockhomes.permissions.homemanage")) {
                    sender.sendErrorMessage("You don't have any permission to use this command!");
                    return false;
                }
                target = args[0];
            }
            std::vector<std::vector<std::string>> homes = api->getHomesList(target);
            if (homes.empty()) {
                sender.sendMessage("You don't have any home points!");
                return true;
            }
            std::string homeNames;
            for (size_t i = 0; i < homes.size(); ++i) {
                if (i > 0) {
                    homeNames += ", ";
                }
                homeNames += homes[i][1];
            }
            sender.sendMessage("Home points: " + homeNames);
            return true;
        }
        if (command.getName() == "sethome") {
            endstone::Player *player = sender.asPlayer();
            if (!player) {
                sender.sendErrorMessage("Only players can use this command!");
                return false;
            }
            if (args.empty()) {
                sender.sendErrorMessage(command.getUsages()[0]);
                return false;
            }
            std::string target = player->getName();
            if (args.size() > 1) {
                if (!sender.hasPermission("white.endstone.bedrockhomes.permissions.homemanage")) {
                    sender.sendErrorMessage("You don't have any permission to use this command!");
                    return false;
                }
                target = args[1];
            }
            endstone::Location location = player->getLocation();
            std::string dimension = player->getDimension().getName();
            std::string position =
                std::to_string(location.getX()) + ":" +
                std::to_string(location.getY()) + ":" +
                std::to_string(location.getZ());
            api->createHome(target, args[0], position, dimension);
            sender.sendMessage("You created '" + args[0] + "' home point");
            return true;
        }
        if (command.getName() == "delhome") {
            endstone::Player *player = sender.asPlayer();
            if (!player) {
                sender.sendErrorMessage("Only players can use this command!");
                return false;
            }
            if (args.empty()) {
                sender.sendErrorMessage(command.getUsages()[0]);
                return false;
            }
            std::string target = player->getName();
            if (args.size() > 1) {
                if (!sender.hasPermission("white.endstone.bedrockhomes.permissions.homemanage")) {
                    sender.sendErrorMessage("You don't have any permission to use this command!");
                    return false;
                }
                target = args[1];
            }
            api->deleteHome(target, args[0]);
            sender.sendMessage("You removed '" + args[0] + "' home point");
            return true;
        }
        return false;
    }
};
