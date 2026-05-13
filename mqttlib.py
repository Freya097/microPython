import json
from umqtt.simple import MQTTClient

# ==================================================
# GLOBAL VARIABLES
# ==================================================

_client = None

BROKER = ""
CLIENT_ID = ""

SUB_TOPIC = b""

PUB_TOPIC = b""

_callback = None

# ==================================================
# MQTT CONFIG
# ==================================================

def setMQTT(
        broker,
        client_id,
        sub_topic,
        pub_topic):

    global BROKER
    global CLIENT_ID
    global SUB_TOPIC
    global PUB_TOPIC

    BROKER = broker

    CLIENT_ID = client_id

    SUB_TOPIC = sub_topic.encode()

    PUB_TOPIC = pub_topic.encode()

# ==================================================
# CALLBACK SET
# ==================================================

def setCallback(callback):

    global _callback

    _callback = callback

# ==================================================
# MQTT CONNECT
# ==================================================

def connect():

    global _client

    _client = MQTTClient(
        CLIENT_ID,
        BROKER,
        port=1883
    )

    if _callback:

        _client.set_callback(_callback)

    _client.connect()

    _client.subscribe(SUB_TOPIC)

    print("MQTT Connected")

# ==================================================
# MQTT PUBLISH JSON
# ==================================================

def publish(data):

    json_data = json.dumps(data)

    _client.publish(
        PUB_TOPIC,
        json_data
    )

# ==================================================
# CHECK MESSAGE
# ==================================================

def check():

    _client.check_msg()
