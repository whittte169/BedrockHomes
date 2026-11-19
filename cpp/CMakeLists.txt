cmake_minimum_required(VERSION 3.15)

project(BedrockHomes VERSION 1.0.1 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(ENDSTONE_API_VERSION "0.11" CACHE STRING "Endstone API version")
set(FETCHCONTENT_QUIET OFF)

include(FetchContent)

FetchContent_Declare(
        sqlite3
        GIT_REPOSITORY https://github.com/clibs/sqlite
        GIT_TAG master
        GIT_SHALLOW TRUE
        GIT_PROGRESS TRUE
)

FetchContent_Declare(
        sqlite_modern_cpp
        GIT_REPOSITORY https://github.com/SqliteModernCpp/sqlite_modern_cpp
        GIT_TAG v3.2
        GIT_SHALLOW TRUE
        GIT_PROGRESS TRUE
)

FetchContent_Declare(
        endstone
        GIT_REPOSITORY https://github.com/EndstoneMC/endstone.git
        GIT_TAG v${ENDSTONE_API_VERSION}
        GIT_SHALLOW TRUE
        GIT_PROGRESS TRUE
)
FetchContent_MakeAvailable(endstone sqlite3 sqlite_modern_cpp)

string(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UPPER)
configure_file(include/version.hpp.in include/version.hpp)

endstone_add_plugin(${PROJECT_NAME} 
        src/main.cpp 
        ${sqlite3_SOURCE_DIR}/sqlite3.c
)
target_include_directories(
        ${PROJECT_NAME} PRIVATE include 
        ${CMAKE_CURRENT_BINARY_DIR}/include
        ${sqlite_modern_cpp_SOURCE_DIR}/hdr
        ${sqlite3_SOURCE_DIR}
)
