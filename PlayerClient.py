import os
import json
from dotenv import load_dotenv
import time
import random
import paho.mqtt.client as paho
from paho import mqtt

from pydantic import ValidationError
from InputTypes import NewPlayer

MOVE_CHOICES = ["UP", "DOWN", "LEFT", "RIGHT"]

def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)

def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_message(client, userdata, msg):
    print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')

    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player2", userdata=None, protocol=paho.MQTTv5)

    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(username, password)
    client.connect(broker_address, broker_port)

    client2.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client2.username_pw_set(username, password)
    client2.connect(broker_address, broker_port)

    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_publish = on_publish

    client2.on_subscribe = on_subscribe
    client2.on_message = on_message
    client2.on_publish = on_publish

    client.loop_start()
    client2.loop_start()

    lobby_name = "TestLobby"
    player_1 = "Player1"
    player_2 = "Player2"
    player_3 = "Player3"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    try:
        client.publish("new_game", NewPlayer(lobby_name=lobby_name, team_name='ATeam', player_name=player_1).json())
        client.publish("new_game", NewPlayer(lobby_name=lobby_name, team_name='BTeam', player_name=player_2).json())
        client.publish("new_game", NewPlayer(lobby_name=lobby_name, team_name='BTeam', player_name=player_3).json())

        time.sleep(1)

        client.publish(f"games/{lobby_name}/start", "START")

        while True:
            move = input("Enter move (UP/DOWN/LEFT/RIGHT): ").strip().upper()
            if move not in MOVE_CHOICES:
                print("Invalid move. Choose from UP, DOWN, LEFT, RIGHT.")
                continue

            client.publish(f"games/{lobby_name}/{player_1}/move", move)
            client.publish(f"games/{lobby_name}/{player_2}/move", move)
            client.publish(f"games/{lobby_name}/{player_3}/move", move)

            if input("Do you want to stop the game? (Y/N): ").strip().upper() == "Y":
                client.publish(f"games/{lobby_name}/start", "STOP")
                break

    except ValidationError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
