import os
import json
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
import random



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

def publish_rand_data(client, topic):
    while True:
        random_data = random.randint(0, 100)
        client.publish(topic, random_data)
        time.sleep(3)

if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player1", userdata=None, protocol=paho.MQTTv5)
    client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player2", userdata=None, protocol=paho.MQTTv5)

    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

        # enable TLS for secure connection
    client2.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client2.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client2.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client2.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client2.on_message = on_message
    client2.on_publish = on_publish # Can comment out to not print when publishing to topics

    client.loop_start()
    client2.loop_start()

    lobby_name = "TestLobby"
    player_1 = "Player1"
    player_2 = "Player2"
    player_3 = "Player3"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'ATeam',
                                            'player_name' : player_1}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'BTeam',
                                            'player_name' : player_2}))
    
    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                        'team_name':'BTeam',
                                        'player_name' : player_3}))

    time.sleep(1) # Wait a second to resolve game start
    client.publish(f"games/{lobby_name}/start", "START")
    client.publish(f"games/{lobby_name}/{player_1}/move", "UP")
    client.publish(f"games/{lobby_name}/{player_2}/move", "DOWN")
    client.publish(f"games/{lobby_name}/{player_3}/move", "DOWN")
    client.publish(f"games/{lobby_name}/start", "STOP")

 
    topic_client1 = "client1/random_data"
    topic_client2 = "client2/random_data"

    client.subscribe(topic_client1)
    client2.subscribe(topic_client2)
    last_time = time.time()
    while True:
        client.loop()
        client2.loop()
        
        # Check if 3 seconds have passed
        if time.time() - last_time >= 3:
            # Publish random data from both clients
            random_data_1 = random.randint(0, 100)
            random_data_2 = random.randint(0, 100)
            client.publish(topic_client1, random_data_1)
            client2.publish(topic_client2, random_data_2)
            print(f"Published {random_data_1} to {topic_client1}")
            print(f"Published {random_data_2} to {topic_client2}")
            
            # Reset the timer
            last_time = time.time()