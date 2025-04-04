import json
import os
import time

from dotenv import load_dotenv

import paho.mqtt.client as mqtt
import pyfimptoha.homeassistant as homeassistant


class Client:
    def __init__(self):
        load_dotenv()

        self.connected: bool = False
        self._server: str = os.environ.get('FIMP_SERVER')
        self._username: str = os.environ.get('FIMP_USERNAME')
        self._password: str = os.environ.get('FIMP_PASSWORD')
        self._port: int = int(os.environ.get('FIMP_PORT'))
        self._client_id: str = os.environ.get('CLIENT_ID')
        self._debug: bool = os.environ.get('DEBUG')
        self._selected_devices_mode: str = os.environ.get('SELECTED_DEVICES_MODE')
        self._selected_devices: list = os.environ.get('SELECTED_DEVICES').split(',')
        self._include_mode: bool = os.environ.get('INCLUDE_MODE')
        self._include_shortcuts: bool = os.environ.get('INCLUDE_SHORTCUTS')
        self._topic_discover: str = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"

        if self._debug.lower() == "true":
            self._debug = True
        else:
            self._debug = False

        if self._include_mode.lower() == "true":
            self._include_mode = True
        else:
            self._include_mode = False

        if self._include_shortcuts.lower() == "true":
            self._include_shortcuts = True
        else:
            self._include_shortcuts = False

        print('Connecting to: ' + self._server)
        print('Username: ', self._username)
        print('Port: ', self._port)
        print('Client id: ', self._client_id)
        print('Debug: ', self._debug)
        print('Selected devices mode: ', self._selected_devices_mode)
        print('Selected devices: ', self._selected_devices)
        print('Include mode: ', self._include_mode)
        print('Include shortcuts: ', self._include_shortcuts)

        self.do_connect()


    def do_connect(self):
        self.client = mqtt.Client(self._client_id)
        self.client.loop_start()

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        self.client.username_pw_set(self._username, self._password)
        self.client.connect(self._server, self._port, 60)
        time.sleep(2)


    def on_connect(self, client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            self.connected = True
            print("MQTT client: Connected successfully")

            # Subscribe to Home Assistant status where Home Assistant announces restarts
            self.client.subscribe("homeassistant/status")

            # Request FIMP devices
            self.client.subscribe(self._topic_discover)

            self.send_discovery_request()


    def send_discovery_request(self):
        """
        Load FIMP devices from MQTT broker
        """
        path = "pyfimptoha/data/fimp_discover.json"
        topic = "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
        with open(path) as json_file:
            data = json.load(json_file)

        payload = json.dumps(data)
        print('Asking FIMP to expose all devices, shortcuts, rooms and mode...')
        self.client.publish(topic, payload)


    def on_message(self, client, userdata, msg):
        """
        The callback for when a message is received from the server.
        """
        payload = str(msg.payload.decode("utf-8"))

        # Discover FIMP devices, shortcuts, mode and create Home Aassistant components out of them
        if msg.topic == self._topic_discover:
            data = json.loads(payload)
            homeassistant.create_components(
                devices=data["val"]["param"]["device"],
                rooms=data["val"]["param"]["room"],
                shortcuts=data["val"]["param"]["shortcut"],
                mode=data["val"]["param"]["house"]["mode"],
                mqtt=self.client,
                selected_devices_mode=self._selected_devices_mode,
                selected_devices=self._selected_devices,
                debug=self._debug,
                include_mode=self._include_mode,
                include_shortcuts=self._include_shortcuts
            )
        elif msg.topic == "homeassistant/status" and payload == "online":
            # Home Assistant was restarted - Push everything again
            self.send_discovery_request()


    def on_disconnect(self, client, userdata, rc):
        """
        The callback for when the client disconnects from the server.
        """

        self.connected = False
        print(f"MQTT client: Disconnected... Result code: {str(rc)}.")
        time.sleep(5)
        self.do_connect()
