import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time


# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)
    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/{player_name}/game_state")
    client.subscribe(f"games/{lobby_name}/scores")


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """

    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    
# Assign the callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Start the loop to process received messages
client.loop_start()

# Game setup variables
lobby_name = "TestLobby"  # This should be unique to your session
player_name = "Player1"  # This should be unique to your player

# Publish the new game command to join the lobby
client.publish("new_game", json.dumps({
    'lobby_name': lobby_name,
    'team_name': 'ATeam',
    'player_name': player_name
}), qos=1)

# Wait a second for the new game command to be processed by the server
time.sleep(1)

# Publish a start command to begin the game
client.publish(f"games/{lobby_name}/start", "START", qos=1)

# Allow the player to make moves based on user input
try:
    while True:
        move_command = input("Enter your move (UP, DOWN, LEFT, RIGHT, or EXIT to quit): ").upper()
        if move_command in ["UP", "DOWN", "LEFT", "RIGHT"]:
            client.publish(f"games/{lobby_name}/{player_name}/move", move_command, qos=1)
        elif move_command == "EXIT":
            print("Exiting game.")
            break
        else:
            print("Invalid command.")
except KeyboardInterrupt:
    print("Game interrupted by user.")

# Stop the loop and disconnect
client.loop_stop()
client.disconnect()
