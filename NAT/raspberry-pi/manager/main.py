from paho.mqtt import client as mqtt_client
import random
import time
import logging
from influxdb_client import InfluxDBClient
import influxdb_client
import json
BROKER = 'mqtt-broker'
PORT = 1883
TOPIC = "raspberry"
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

INFLUXDB_URL = 'http://g3.south-squad.io:8086'
INFLUXDB_TOKEN = 'oFn446lJumcISf9hSY-zpiyPtyjGyVRzsRTTZ7L3lPeLtBa_reF0USZGVM0HLCVmUT_tio0Rug1RdDsec45hsg=='
# username = 'emqx'
# password = 'public'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(client, userdata, rc):
        logging.info("Disconnected with result code: %s", rc)
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logging.info("Reconnecting in %d seconds...", reconnect_delay)
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logging.info("Reconnected successfully!")
                return
            except Exception as err:
                logging.error("%s. Reconnect failed. Retrying...", err)

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    # Set Connecting Client ID
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, CLIENT_ID)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    # client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(BROKER, PORT)
    return client


def subscribe_to_all(client: mqtt_client):
    inf_client = connect_influxdb()
    def on_message(client, userdata, message):
        decoded_payload = message.payload.decode()
        decoded_payload = json.loads(decoded_payload)
        #payload format {"mac": "mac adress", "value": "floating point value", "timestamp": "timestamp"}
        print(f"Received `{decoded_payload}` from `{message.topic}` topic")
        print(f"Message received: {message.payload}")
        data = {
            "measurement": message.topic,
            "fields": {
                "mac": decoded_payload["mac"],
                "value": float(decoded_payload["value"])
            },
            "time": decoded_payload["timestamp"]
        }
        write_to_influxdb(inf_client, data)

    client.subscribe('#')
    client.on_message = on_message

def connect_influxdb():
    inf_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org='docs')
    inf_client.setKeepAlive(0)
    return inf_client

def write_to_influxdb(inf_client: InfluxDBClient, data):
    write_api = inf_client.write_api()
    record = influxdb_client.Point("raspberry").tag("mac", data["fields"]["mac"]).tag("measurement", data["measurement"]).field("value", data["fields"]["value"]).time(data["time"])
    write_api.write(bucket='raspberry', record=record, org='docs')
    print(f"Data written to InfluxDB: {record}")



mqtt_client = connect_mqtt()
mqtt_client.loop_start()
subscribe_to_all(mqtt_client)





while True:
    time.sleep(1)