import os
import time
import random
import json
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
client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Client1", userdata=None, protocol=paho.MQTTv5)
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(username, password)


# Callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")

def on_publish(client, userdata, mid):
    print("mid: " + str(mid))

client.on_connect = on_connect

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

client.loop_start()

while True:
    # Publish random data to the unique topic every 3 seconds
    client.publish("client2/data", payload=random.randint(0, 100))
    time.sleep(3)
