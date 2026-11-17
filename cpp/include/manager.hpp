#pragma once

#include <endstone/endstone.hpp>
#include <string>
#include <vector>
#include <exception>
#include <filesystem>
#include <sqlite_modern_cpp.h>

class HomeManager {
private:
    sqlite::database database;
    endstone::Plugin &plugin;
public:
    explicit HomeManager(endstone::Plugin &plugin) : plugin(plugin), database(loadDatabase(plugin)) {
        try {
            database << "PRAGMA journal_mode=WAL";
            database << "PRAGMA synchronous=NORMAL";
            database << "CREATE TABLE IF NOT EXISTS homes (name TEXT, home TEXT, position TEXT, dimension TEXT)";
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
        }
    }

    std::vector<std::string> selectHome(const std::string &name, const std::string &home) {
        std::vector<std::string> homeVector;
        try {
            database << "SELECT name, home, position, dimension FROM homes WHERE name = ? AND home = ?;"
                << name << home
                >> [&](std::string resName, std::string resHome, std::string position, std::string dimension) {
                    homeVector = {
                        std::move(resName),
                        std::move(resHome),
                        std::move(position),
                        std::move(dimension)
                    };
                };
            return homeVector;
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
            return homeVector;
        }
    }

    std::vector<std::vector<std::string>> getHomesList(const std::string &name) {
        std::vector<std::vector<std::string>> homesList;
        try {
            database << "SELECT name, home, position, dimension FROM homes WHERE name = ?;"
                    << name
                    >> [&](std::string resName, std::string resHome, std::string position, std::string dimension) {
                    homesList.push_back({
                        std::move(resName),
                        std::move(resHome),
                        std::move(position),
                        std::move(dimension)
                    });
                };
            return homesList;
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
            return {};
        }
    }

    void createHome(std::string name, std::string home, std::string position, std::string dimension) {
        try {
            database << "INSERT OR IGNORE INTO homes (name, home, position, dimension) VALUES (?, ?, ?, ?);"
            << name, home, position, dimension;
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
        }
    }

    void deleteHome(std::string name, std::string home) {
        try {
            database << "DELETE FROM homes WHERE name = ? AND home = ?;"
            << name, home;
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
        }
    }
    
private:
    static sqlite::database loadDatabase(endstone::Plugin &plugin) {
        try {
            const auto &dataFolder {plugin.getDataFolder()};
            if (!std::filesystem::exists(dataFolder)) {
                std::filesystem::create_directories(dataFolder);
            }
            std::filesystem::path dbPath {dataFolder / "database.db"};
            return sqlite::database(dbPath.string());
        } catch (const std::exception &e) {
            plugin.getLogger().error(std::string("Failed to load database! ") + e.what());
            throw;
        }
    }
};