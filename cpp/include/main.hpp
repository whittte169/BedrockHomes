#pragma once

#include <endstone/endstone.hpp>

class Main : public endstone::Plugin {
public:
    void onEnable() override {
        getLogger().info("BedrockHomes was successfully loaded!");
        getLogger().info("GitHub: " + endstone::ColorFormat::Green + "https://github.com/whittte169/BedrockHomes" + endstone::ColorFormat::Reset);
    }
};