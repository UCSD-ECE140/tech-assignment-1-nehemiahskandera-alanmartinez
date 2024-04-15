import os
import paho.mqtt.client as paho
from dotenv import load_dotenv
from paho import mqtt

# Load environment variables
load_dotenv(dotenv_path='./credentials.env')

# MQTT Broker settings
broker_address = os.getenv('BROKER_ADDRESS')
broker_port = int(os.getenv('BROKER_PORT'))
username = os.getenv('USER_NAME')
password = os.getenv('PASSWORD')

# Initialize the MQTT client
client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client2", userdata=None, protocol=paho.MQTTv5)
client.username_pw_set(username, password)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

def on_connect(client, userdata, flags, rc, properties=None):
    print("Connected with result code " + str(rc))
    # Subscribe to both topics
    client.subscribe("client1/data")
    client.subscribe("client2/data")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
client.loop_forever()
