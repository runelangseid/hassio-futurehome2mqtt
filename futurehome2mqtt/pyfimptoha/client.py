import json, time
import paho.mqtt.client as mqtt
import requests, threading
from pyfimptoha.mode import Mode

class Client:

    _devices = [] # discovered fimp devices
    _mqtt = None
    _selected_devices = None
    _topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
    _topic_fimp_event = "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/"
    _topic_ha = "homeassistant/"
    _verbose = False

    def __init__(self, mqtt=None, selected_devices=None, token=None, ha_host=None, debug=False):
        self._selected_devices = selected_devices
        self._verbose = debug

        if mqtt:
            self._mqtt = mqtt
            mqtt.on_message = self.on_message

        self.start()

    def log(self, s, verbose = False):
        '''Log'''
        if verbose and not self._verbose:
            return
        print(s)

    def start(self):
        # Add Modus sensor (home, sleep, away and vacation)
        # todo Find a way to auto discover the value. Sensor value is currently
        # empty until changed by the system/user

        mode = Mode()
        message = mode.get_component()
        self.publish_messages([message])

        # fimp discover
        self.send_fimp_discovery()

        # subscribe to home assistant status where ha announces restarts
        self._mqtt.subscribe("homeassistant/status")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode("utf-8"))

        # Discover FIMP devices and create HA components out of them
        if msg.topic == self._topic_discover:
            data = json.loads(payload)
            self.create_components(data["val"]["param"]["device"])
        elif msg.topic == "homeassistant/status" and payload == "online":
            print(msg.topic)
            self.start()

    def publish_messages(self, messages):
        """Publish list of messages over MQTT"""
        if self._verbose:
            print('Publish messages', messages)

        if self._mqtt and messages:
            for data in messages:
                self._mqtt.publish(data["topic"], data["payload"])

    def send_fimp_discovery(self):
        """Load FIMP devices from MQTT broker"""

        path = "pyfimptoha/data/fimp_discover.json"
        topic = "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
        with open(path) as json_file:
            data = json.load(json_file)

            # Subscribe to : pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1
            self._mqtt.subscribe(self._topic_discover)
            message = {
                'topic': topic,
                'payload': json.dumps(data)
            }
            self.log('Asking FIMP to expose all devices...')
            self.publish_messages([message])

    def load_json_device(self, filename):
        data = "{}"

        path = "pyfimptoha/data/%s" % filename
        with open(path) as json_file:
            data = json.load(json_file)
        self._devices.append(data)

    def create_components(self, devices):
        """
        Creates HA components out of FIMP devices
        by pushing them to HA using mqtt discovery
        """
        self._devices = devices
        self.log('Received list of devices from FIMP. FIMP reported %s devices' % (len(devices)))
        self.log('Devices without rooms are ignored')

        statuses = []

        # todo Add support for Wall plugs with functionality 'Lighting'

        for device in self._devices:
            address = device["fimp"]["address"]
            name = device["client"]["name"]
            functionality = device["functionality"]
            room = device["room"]

            # Skip device without room
            if device["room"] == None:
                # self.log('Skipping: %s %s' % (address, name))
                continue

            #  When debugging: Ignore everything except self._selected_devices if set
            if self._selected_devices and address not in self._selected_devices:
                self.log('Skipping: %s %s' % (address, name))
                continue

            self.log("Creating: %s %s" % (address, name))
            self.log("- Functionality: %s" % (functionality))

            #if address != '21':
            #   continue

            for service_name in device["services"]:
                # Service meter_elec - "Forbruk"
                if service_name == "meter_elec":
                    identifier = f"fh_{address}_meter_elec"
                    state_topic = f"pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:meter_elec/ad:{address}_0"
                    component = {
                        "name": f"{device['client']['name']} (forbruk)",
                        "object_id": identifier,
                        "unique_id": identifier,
                        "state_topic": state_topic,
                        "device_class": "energy",
                        "state_class": "total_increasing",
                        "unit_of_measurement": "kWh",
                        "value_template": "{{ value_json.val }}"
                    }
                    payload = json.dumps(component)
                    self._mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

                    # Queue statuses
                    if device.get("param") and device['param'].get('energy'):
                        value = device['param']['energy']
                        data = {
                            "props": {
                                "unit": "kWh"
                            },
                            "serv": "meter_elec",
                            "type": "evt.meter.report",
                            "val": value,
                        }

                        payload = json.dumps(data)
                        statuses.append((state_topic, payload))

                # Lights
                elif functionality == "lighting":
                    # todo Add support for bin switch
                    if service_name == "out_lvl_switch":
                        identifier = f"fh_{address}_{service_name}"
                        command_topic = f"pt:j1/mt:cmd/rt:dev/rn:zw/ad:1/sv:out_lvl_switch/ad:{address}_1"
                        state_topic = f"pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_lvl_switch/ad:{address}_1"
                        component = {
                            "name": f"{device['client']['name']}",
                            "object_id": identifier,
                            "unique_id": identifier,
                            "schema": "template",
                            "command_topic": command_topic,
                            "state_topic": state_topic,
                            "brightness_scale": 100,
                            "command_on_template": """
                                {
                                  "props":{},
                                  "serv":"out_lvl_switch",
                                  "tags":[]
                                {%- if brightness -%}
                                  , "type":"cmd.lvl.set",
                                  "val":{{ (brightness / 2.55) | int }},
                                  "val_t":"int"
                                {%- else -%}
                                  , "type":"cmd.binary.set",
                                  "val":true,
                                  "val_t":"bool"
                                {%- endif -%}
                                }
                            """,
                            "command_off_template": """
                                {"props":{},
                                  "serv":"out_lvl_switch",
                                  "tags":[],
                                  "type":"cmd.binary.set",
                                  "val":false,
                                  "val_t":"bool"}
                            """,
                            "state_template": "{% if value_json.val %} on {% else %} off {% endif %}",
                            "brightness_template": "{% if value_json.val_t %}{{ (value_json.val * 2.55) | int }}{% endif %}"
                        }
                        payload = json.dumps(component)
                        self._mqtt.publish(f"homeassistant/light/{identifier}/config", payload)

                        # Queue statuses
                        if device.get("param") and device['param'].get('power'):
                            power = device['param']['power']
                            if power == "off":
                                data = {
                                    "props": {},
                                    "serv": "out_lvl_switch",
                                    "type": "cmd.binary.report",
                                    "val_t": "bool",
                                    "val": False
                                }
                            else:
                                dim_value = device['param']['dimValue']
                                data = {
                                    "props": {},
                                    "serv": "out_lvl_switch",
                                    "type": "cmd.lvl.report",
                                    "val_t": "int",
                                    "val": dim_value
                                }
                            payload = json.dumps(data)
                            statuses.append((state_topic, payload))

                # todo Add support for binary_sensor?

        self._mqtt.loop()
        time.sleep(2)
        self.log("Publishing statuses...")
        for state in statuses:
            topic = state[0]
            payload = state[1]
            self._mqtt.publish(topic, payload)
            self.log(topic)
        self.log("Finished pushing statuses...")

    def listen_fimp(self):
        """
        Enables listening on FIMP event topics
        """
        self._listen_fimp_event = True
        self._mqtt.subscribe(self._topic_fimp_event + "#")

