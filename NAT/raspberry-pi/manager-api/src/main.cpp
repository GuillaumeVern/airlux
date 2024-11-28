#include <paho.mqtt.cpp>
#include <iostream>

int main() {
    mqtt::client cli("tcp://localhost:1883", "manager-api");
    cli.connect();
    cli.publish("raspberry-pi/manager-api", "Hello, World!");
    cli.disconnect();
    return 0;
}