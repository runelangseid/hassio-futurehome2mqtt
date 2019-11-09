import json, time
import paho.mqtt.client as mqtt
from pyfimptoha.light import Light

class Client:
    components = {}
    lights = []

    _devices = [] # discovered fimp devices
    _mqtt = None
    _topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
    _topic_fimp_event = "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/"
    _topic_ha = "homeassistant/"
    _components = None
    _listen_ha = False
    _listen_fimp_event = False

    def __init__(self, mqtt=None):
        if mqtt:
            self._mqtt = mqtt
            mqtt.on_message = self.on_message

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode("utf-8"))

        # Discover FIMP devices and create HA components out of them
        if msg.topic == self._topic_discover:
            data = json.loads(payload)
            self.create_components(data["val"]["param"]["device"])

        # Received commands from HA
        elif msg.topic.startswith(self._topic_ha):
            self.process_ha(msg.topic, payload)

        # Received event from FIMP - Update HA state_topic
        # pt:j1/mt:evt/rt:dev/rn:zw/ad:1/
        elif msg.topic.startswith(self._topic_fimp_event):
            # print('Got fimp event !')
            messages = self.process_fimp_event(msg.topic, payload)
            self.publish_messages(messages)

    def publish_messages(self, messages):
        """Publish list of messages over MQTT"""
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
            self._mqtt.publish(topic, json.dumps(data))

    def publish_components(self):
        """
        Publish components and their initial states
        """

        # - Lights
        for light in self.lights:
            # todo Add support for Wall plugs with functionality 'Lighting'

            # debug Exclude all but light 7
            # if light._address != "7":
            #     continue

            component = light.get_component()

            # print("Publishing lights")
            # print("- Unique id", light._address, light._unique_id)
            # print("- component", component)

            # Create light component
            self._mqtt.publish(component["topic"], component["payload"])

        # Publish init states
        print("Publishing lights init state")
        time.sleep(0.5)
        for light in self.lights:
            init_state = light.get_state()
            for data in init_state:
                self._mqtt.publish(data["topic"], data["payload"])
                time.sleep(0.1)

    def load_json_device(self, filename):
        data = "{}"

        path = "pyfimptoha/data/%s" % filename
        with open(path) as json_file:
            data = json.load(json_file)
        self._devices.append(data)

    def create_components(self, devices):
        """ Creates HA components out of FIMP devices"""
        discovery = list()
        self._devices = devices

        for device in self._devices:
            # Skip device without room
            if device["room"] == None:
                continue

            address = device["fimp"]["address"]
            name = device["client"]["name"]
            functionality = device["functionality"]
            room = device["room"]

            for service_name in device["services"]:
                supported_services = ["sensor_power", "out_lvl_switch"]
                service = device["services"][service_name]
                if service_name not in supported_services:
                    continue

                component_address = address + "-" + service_name

                # Figure out ha component
                component = None
                if service_name.startswith("sensor_"):
                    component = "sensor"
                elif service_name.startswith("battery"):
                    component = "sensor"
                elif (
                    service_name.startswith("out_lvl_switch")
                    and functionality == "lighting"
                ):
                    component = "light"

                # Generate ha device
                # topic: homeassistant/light/7_sensor_power/config
                topic = "homeassistant/%s/%s/config" % (component, component_address)

                payload = {
                    "name": "%s (%s)" % (name, service_name),
                    "state_topic": topic.replace("config", "state"),
                }

                if component == "sensor":
                    unit = service["props"]["sup_units"][0]
                    payload["unit_of_measurement"] = unit
                elif component == "light":
                    light = Light(service_name, service, device)
                    self.lights.append(light)
                    self.components[light.unique_id] = light

                new_device = {
                    "topic": topic,
                    "payload": json.dumps(payload),
                }
                discovery.append(new_device)

        self._components = discovery
        return discovery

    def process_ha(self, topic, payload):
        """
        Process a message from ha and generates one to FIMP

        Eg: 
        - Topic: homeassistant/light/7-out_lvl_switch/set
        - Payload: ON

        Or set dimmer level
        - Topic: homeassistant/light/7-out_lvl_switch/command
        - Payload: 33
        """

        topic = topic.split("/")
        result = None

        # Topic like: homeassistant/light/7-out_lvl_switch/command
        if len(topic) > 3:
            # print("process_ha:topic", topic)
            component = topic[1]
            unique_id = topic[2]
            topic_type = topic[3]

            if component == "light":
                for light in self.lights:
                    if light.unique_id == unique_id:
                        messages = light.handle_ha(topic_type, payload)

                        print("messages", messages)
                        self.publish_messages(messages)

        return

    def process_fimp_event(self, topic, payload):
        """
        Process a message from FIMP and generates one to HA

        Eg: Dimmer update
        - Topic: pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_lvl_switch/ad:7_1

        """
        topic = topic.split("/")
        payload = json.loads(payload)

        if len(topic) > 6:
            tmp, type = topic[1].split(":", 1) # evt or cmd
            tmp, service_name = topic[5].split(":", 1) # out_lvl_switch, sensor_power, etc
            tmp, address = topic[6].split(":", 1)
            address, tmp = address.split("_", 1) # device address: 1 or higher
            unique_id = address + "-" + service_name

            # debug Exclude all but light 7
            # if address != "7":
            #     return None

            component = self.components.get(unique_id)
            if not component:
                return None

            data = component.handle_fimp(payload)
            return data

        return None

    def listen_ha(self):
        """
        Enables listening on HA topics
        """
        self._listen_ha = True
        self._mqtt.subscribe(self._topic_ha + "#")

    def listen_fimp(self):
        """
        Enables listening on FIMP event topics
        """
        self._listen_fimp_event = True
        self._mqtt.subscribe(self._topic_fimp_event + "#")

