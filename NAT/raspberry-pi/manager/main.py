from paho.mqtt import client as mqtt_client
import random
import time
import logging
import redis
from redis.commands.json.path import Path
from influxdb_client import InfluxDBClient
import influxdb_client
import json
BROKER = 'mqtt-broker'
PORT = 1883
TOPIC = "raspberry"
CLIENT_ID = f'python-mqtt-{random.randint(0, 1000)}'

INFLUXDB_URL = 'http://g3.south-squad.io:8086'
INFLUXDB_TOKEN = 'vmz7HmKYyw3titaT8wtLpq6F_saDgk3s0HhFJxGikPRPDrzTSB68VTZ43ux_5ihe-FkbKrNf4cCkE1ndpl2klg==' #'oFn446lJumcISf9hSY-zpiyPtyjGyVRzsRTTZ7L3lPeLtBa_reF0USZGVM0HLCVmUT_tio0Rug1RdDsec45hsg=='
# username = 'emqx'
# password = 'public'

REDIS_HOST = 'redis-cache'
REDIS_PORT = 6379

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 99999999
MAX_RECONNECT_DELAY = 30

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
        while reconnect_count < MAX_RECONNECT_COUNT and not client.is_connected():
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
    red_client = connect_redis()
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
        printf(inf_client.ping())
        printf(inf_client.health())
        if inf_client.health().status == 'passing':
            for key in red_client.scan_iter():
                result = red_client.json().get(key)
                red_client.delete(key)
                if result:
                    write_to_influxdb(inf_client, result)
            write_to_influxdb(inf_client, data)
        else:
            write_to_redis(red_client, data)

    client.subscribe('#')
    client.on_message = on_message

def connect_influxdb():
    inf_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org='docs')
    return inf_client

def write_to_influxdb(inf_client: InfluxDBClient, data):
    write_api = inf_client.write_api()
    record = influxdb_client.Point("raspberry").tag("mac", data["fields"]["mac"]).tag("measurement", data["measurement"]).field("value", data["fields"]["value"]).time(data["time"])
    write_api.write(bucket='raspberry', record=record, org='docs')
    print(f"Data written to InfluxDB: {record}")

def connect_redis():
    red_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    return red_client

def write_to_redis(red_client: redis.Redis, data):
    key = data["fields"]["mac"] + '_' + data["time"]
    record = red_client.json().set(key, Path.root_path(), data)
    print(f"Data written to Redis: {record}")


mqtt_client = connect_mqtt()
mqtt_client.loop_start()
subscribe_to_all(mqtt_client)





while True:
    time.sleep(1)