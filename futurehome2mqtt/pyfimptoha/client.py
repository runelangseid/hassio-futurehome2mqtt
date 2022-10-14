import json

import pyfimptoha.fimp as fimp
import pyfimptoha.homeassistant as homeassistant
import pyfimptoha.mode as mode


class Client:
    _devices = [] # discovered fimp devices
    _mqtt = None
    _selected_devices = None
    _topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
    _topic_fimp_event = "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/"
    _topic_ha = "homeassistant/"
    _verbose = False

    def __init__(
            self,
            mqtt=None,
            selected_devices=None,
            debug=False
    ):
        self._selected_devices = selected_devices
        self._verbose = debug

        if mqtt:
            self._mqtt = mqtt
            mqtt.on_message = self.on_message

        self.start()

    def start(self):
        mqtt = self._mqtt

        # Create mode sensor  (home, away , sleep and vacation)
        # todo Find a way to auto discover the value. Sensor value is currently
        # empty until changed by the system/user
        mode.publish(mqtt)

        # Send FIMP discover request
        topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
        mqtt.subscribe(topic_discover)
        fimp.send_discovery_request(mqtt)

        # Subscribe to home assistant status where ha announces restarts
        self._mqtt.subscribe("homeassistant/status")

    def on_message(self, client, userdata, msg):
        """
        The callback for when a message is received from the server.
        """
        payload = str(msg.payload.decode("utf-8"))

        # Discover FIMP devices and create HA components out of them
        if msg.topic == self._topic_discover:
            data = json.loads(payload)
            homeassistant.create_components(
                devices=data["val"]["param"]["device"],
                mqtt=self._mqtt,
                selected_devices=self._selected_devices,
            )
        elif msg.topic == "homeassistant/status" and payload == "online":
            print(msg.topic)
            self.start()
