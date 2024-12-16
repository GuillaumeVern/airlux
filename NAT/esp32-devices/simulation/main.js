require('dotenv').config(); // Add this line to load environment variables from .env file

const mqtt = require('mqtt');

// Environment variables
const MQTT_BROKER_URL = process.env.MQTT_BROKER_URL || 'mqtt://localhost';
const MQTT_USERNAME = process.env.MQTT_USERNAME || '';
const MQTT_PASSWORD = process.env.MQTT_PASSWORD || '';
const DATA_FREQUENCY = parseInt(process.env.DATA_FREQUENCY, 10) || 5000; // in milliseconds
const SENSOR_COUNT = parseInt(process.env.SENSOR_COUNT, 10) || 4;
const MQTT_QOS = parseInt(process.env.MQTT_QOS, 10) || 0;

// Simulated sensors
let sensors = [
    {
        name: 'temperature',
        value: 20,
        min: 15,
        max: 25,
        mac: generateRandomMacAddress()
    },
    {
        name: 'humidity',
        value: 50,
        min: 30,
        max: 70,
        mac: generateRandomMacAddress()
    },
    {
        name: 'luminosity',
        value: 300,
        min: 100,
        max: 500,
        mac: generateRandomMacAddress()
    },
    {
        name: 'pressure',
        value: 1013,
        min: 980,
        max: 1050,
        mac: generateRandomMacAddress()
    },
    {
        name: 'air_quality',
        value: 100,
        min: 50,
        max: 150,
        mac: generateRandomMacAddress()
    }
];

// Limit the number of sensors based on SENSOR_COUNT
sensors = sensors.slice(0, SENSOR_COUNT);

const options = {
    username: MQTT_USERNAME,
    password: MQTT_PASSWORD
};

const client = mqtt.connect(MQTT_BROKER_URL, options);

client.on('connect', () => {
    console.log(`Connected to MQTT broker at ${MQTT_BROKER_URL}`);
    setInterval(publishSensorData, DATA_FREQUENCY);
});

client.on('error', (error) => {
    console.error('Connection error:', error);
    process.exit(1);
});

function publishSensorData() {
    sensors.forEach(sensor => {
        // Simulate small variations
        const variation = (Math.random() * 2 - 1); // Random value between -1 and 1
        sensor.value = Math.min(Math.max(sensor.value + variation, sensor.min), sensor.max);

        const topic = `sensors/${sensor.name}`;
        const message = JSON.stringify({
            mac: sensor.mac,
            value: sensor.value.toFixed(2),
            timestamp: new Date().toISOString()
        });

        client.publish(topic, message, { qos: MQTT_QOS }, (error) => {
            if (error) {
                console.error(`Failed to publish to ${topic}:`, error);
            } else {
                console.log(`Published to ${topic}: ${message}`);
            }
        });
    });
}

function generateRandomMacAddress() {
    return Array.from({ length: 6 }, () => {
        return Math.floor(Math.random() * 256).toString(16).padStart(2, '0');
    }).join(':');
}