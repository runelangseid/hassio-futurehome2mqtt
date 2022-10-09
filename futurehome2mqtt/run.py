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
        print("MQTT client: Connected successfull")
    else:
        connected = False
        print("MQTT client: Could not connect. Result code: " + str(rc))


def on_disconnect(client, userdata, rc):
    global connected

    connected = False
    print("MQTT client: Disconnected... Result code: " + str(rc))


def do_connect():
    client = mqtt.Client(client_id)
    client.loop_start()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.username_pw_set(username, password)
    client.connect(server, port, 60)
    return client


def serve(client, selected_devices):
    global connected
    f = fimp.Client(
        mqtt=client,
        selected_devices=selected_devices,
        debug=debug
    )

    print("Sleeping forever...")
    while True:
        if not connected:
            print("MQTT client: No longer connected... Exiting")
            break

        time.sleep(10)


if __name__ == "__main__":
    print('Starting service...')

    connected = None
    server = os.environ.get('FIMPSERVER')
    username = os.environ.get('FIMPUSERNAME')
    password = os.environ.get('FIMPPASSWORD')
    port = int(os.environ.get('FIMPPORT'))
    client_id = os.environ.get('CLIENT_ID')
    debug = os.environ.get('DEBUG')
    selected_devices = []

    _selected_devices = os.environ.get('SELECTED_DEVICES')
    if _selected_devices:
        selected_devices = _selected_devices.split(',')

    if debug.lower() == 'true':
        debug = True
    else:
        debug = False

    print('Connection to ' + server)
    print('User: ', username)
    print('Port: ', port)
    print('Client id: ', client_id)
    print('Debug : ', debug)
    print('Selected devices', selected_devices)

    if len(sys.argv) > 1 and sys.argv[1] == "help":
        print(
            'Usage: \n"python run.py serve" to fetch data form fimp and push components to Home Assistant'
        )

    elif len(sys.argv) > 1 and sys.argv[1] == "serve":
        client = do_connect()

        time.sleep(2)

        if connected:
            serve(client, selected_devices)
