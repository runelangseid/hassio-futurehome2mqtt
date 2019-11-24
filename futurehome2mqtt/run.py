import paho.mqtt.client as mqtt
import os, sys, time
import pyfimptoha.client as fimp

"""
todo Refactor these functions, move to pyfimotopa/client.py
"""
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global connected

    if rc == 0:
        connected = True
        print("Connected successfull")
    else:
        connected = False
        print("Could not connect. Result code: " + str(rc))

def on_disconnect(client, userdata, rc):
    global connected

    connected = False
    print("Disconnected... Result code: " + str(rc))

def do_connect():
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.username_pw_set(username, password)
    client.connect(server, port, 60)
    return client

def serve(client, selected_devices):
    global connected
    f = fimp.Client(client, selected_devices, token)

    print("Sleeping forever...")
    while True:
        if not connected:
            print("No longer connected... Exiting")
            break

        time.sleep(10)

# def create_binary_sensor(client):
#     """
#     Test function for creating an binary sensor
#     """
#     t = "homeassistant/binary_sensor/garden/config"
#     p = '{"name": "garden", "device_class": "motion", "state_topic": "homeassistant/binary_sensor/garden/state"}'
#     client.publish(t, p)

#     t = "homeassistant/binary_sensor/garden/state"
#     p = "OFF"
#     client.publish(t, p)

#     time.sleep(3)
#     p = "ON"
#     client.publish(t, p)


if __name__ == "__main__":
    print('Starting service...')

    connected = None
    server = os.environ.get('FIMPSERVER')
    username = os.environ.get('FIMPUSERNAME')
    password = os.environ.get('FIMPPASSWORD')
    port = int(os.environ.get('FIMPPORT'))
    token = os.environ.get('HASSIO_TOKEN')
    client_id = os.environ.get('CLIENT_ID')

    print('Connection to ' + server)
    print('User: ', username)
    print('Port: ', port)
    print('Client id: ', client_id)
    print('Hassio token: ', token[:5] + "...")

    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print(
            'Usage: \n"python run.py serve" to fetch data form fimp and push components to Home Assistant'
        )

    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        client = do_connect()
        client.loop_start()

        time.sleep(2)

        if connected:
            serve(client, None)
            # serve(client, [7, 37])
