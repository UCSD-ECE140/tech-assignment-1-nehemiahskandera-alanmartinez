import os
import json
from dotenv import load_dotenv
import paho.mqtt.client as paho
from paho import mqtt
import time
import random

# Define constants
EMPTY_CELL = '-'
TEAM_A = 'TeamA'
TEAM_B = 'TeamB'

class Map:
    def __init__(self, height, width, players):
        self.height = height
        self.width = width
        self.players = players
        self.map = [['-' for _ in range(width)] for _ in range(height)]

    def __fillMap(self, playersList):
        # Logic to fill the map
        pass

    def __placeRandom(self, item, choice):
        if choice:
            x, y = random.choice(choice)
            self.map[y][x] = item

    def placeWalls(self, wallChoices):
        self.__placeRandom('Wall', wallChoices)

# Callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    # Subscribing to necessary topics
    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f"games/{lobby_name}/game_state")
    client.subscribe(f"games/{lobby_name}/scores")

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == f"games/{lobby_name}/game_state":
        process_game_state(msg.payload.decode())

def on_publish(client, userdata, mid):
    print(f"Message published with mid {mid}")

def on_subscribe(client, userdata, mid, granted_qos, properties=None):  # Modify here
    print("Subscribed:", mid, granted_qos)

def process_game_state(game_state):
    # Convert the game state string to a dictionary
    game_state_dict = json.loads(game_state)
    board = game_state_dict.get('board')
    print_board(board)

def print_board(board):
    # Print the game board
    print("Current Board:")
    for row in board:
        print(" ".join(row))
    print()

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    # Game setup variables
    lobby_name = "TestLobby"  # This should be unique to your session

    # Define player names and team names
    team_names = ["TeamA", "TeamB"]
    player_names = ["Player1", "Player2", "Player3", "Player4"]

    # Shuffle the player names to distribute them evenly among teams
    random.shuffle(player_names)

    # Initialize MQTT clients for each player
    clients = []
    for i, player_name in enumerate(player_names):
        team_name = team_names[i % len(team_names)]
        client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id=f"GameClient_{player_name}", userdata=None, protocol=paho.MQTTv5)        
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_publish = on_publish
        client.on_subscribe = on_subscribe
        clients.append((client, team_name))

    # Connect each client to the MQTT broker
    for client, _ in clients:
        client.connect(broker_address, broker_port)

    # Start the loop to process received messages
    for client, _ in clients:
        client.loop_start()

    # Publish the new game command to join the lobby
    for client, team_name in clients:
        client.publish("new_game", json.dumps({
            'lobby_name': lobby_name,
            'team_name': team_name,
            'player_name': client._client_id.decode()  # Convert bytes to string
        }), qos=1)

    # Wait for the new game command to be processed by the server
    time.sleep(1)

    # Publish a start command to begin the game
    clients[0][0].publish(f"games/{lobby_name}/start", "START", qos=1)

    try:
        while True:
            # Simulate moves for each player
            for client, _ in clients:
                move_command = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
                client.publish(f"games/{lobby_name}/{client._client_id.decode()}/move", move_command, qos=1)
                time.sleep(1)  # Add delay between moves

            time.sleep(10)  # Wait for the game to progress

    except KeyboardInterrupt:
        # Stop the loop and disconnect on keyboard interrupt
        for client, _ in clients:
            client.loop_stop()
            client.disconnect()
