cmake_minimum_required(VERSION 3.31)

include(FetchContent)
project(manager-api)
file(GLOB_RECURSE SOURCES RELATIVE ${CMAKE_SOURCE_DIR} "src/*.c")
add_executable(manager-api ${SOURCES})


FetchContent_Declare(
    paho.mqtt.c
    GIT_REPOSITORY https://github.com/eclipse-paho/paho.mqtt.c
    GIT_TAG v1.3.13
)

FetchContent_Declare(
    paho.mqtt.cpp
    GIT_REPOSITORY https://github.com/eclipse-paho/paho.mqtt.cpp
    GIT_TAG v1.4.1
)

FetchContent_Declare(
    boost.redis
    GIT_REPOSITORY https://github.com/boostorg/redis
    GIT_TAG boost-1.86.0
)
    
FetchContent_MakeAvailable(paho.mqtt.c paho.mqtt.cpp boost.redis)

set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} ${paho.mqtt.c_SOURCE_DIR})

find_package(paho.mqtt.cpp REQUIRED)
find_package(Boost.redis REQUIRED)