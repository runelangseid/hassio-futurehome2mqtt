import json, time
import paho.mqtt.client as mqtt
from pyfimptoha.light import Light
from pyfimptoha.sensor import Sensor

class Client:
    components = {}
    lights = []
    sensors = []

    _devices = [] # discovered fimp devices
    _mqtt = None
    _selected_devices = None
    _topic_discover = "pt:j1/mt:rsp/rt:app/rn:homeassistant/ad:flow1"
    _topic_fimp_event = "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/"
    _topic_ha = "homeassistant/"
    _components = None
    _listen_ha = False
    _listen_fimp_event = False

    def __init__(self, mqtt=None, selected_devices=None):
        self._selected_devices = selected_devices

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
        # print('Publish messages', messages)
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
            self.publish_messages([message])

    def publish_components(self):
        """
        Publish components and their initial states
        """

        # - Lights
        # todo Add support for Wall plugs with functionality 'Lighting'
        for unique_id, component in self.components.items():
            #  Ignore everything except self._selected_devices if set
            if self._selected_devices and int(component._address) not in self._selected_devices:
                continue

            message = component.get_component()
            self.publish_messages([message])

        # Publish init states
        print("Publishing lights init state")
        time.sleep(0.5)
        for light in self.lights:
            init_state = light.get_state()
            for data in init_state:
                self.publish_messages([data])
                time.sleep(0.1)

    def load_json_device(self, filename):
        data = "{}"

        path = "pyfimptoha/data/%s" % filename
        with open(path) as json_file:
            data = json.load(json_file)
        self._devices.append(data)

    def create_components(self, devices):
        """ Creates HA components out of FIMP devices"""
        self._devices = devices

        for device in self._devices:
            # Skip device without room
            if device["room"] == None:
                continue

            address = device["fimp"]["address"]
            name = device["client"]["name"]
            functionality = device["functionality"]
            room = device["room"]

            if self._selected_devices and int(address) not in self._selected_devices:
                continue

            print("Creating: ", address, name)

            for service_name in device["services"]:
                component = None
                component_address = address + "-" + service_name
                service = device["services"][service_name]

                if (
                    service_name.startswith("out_lvl_switch")
                    and functionality == "lighting"
                ):
                    component = "light"
                elif service_name in Sensor.supported_services():
                    component = "sensor"

                if not component:
                    print("- Skipping %s. Not yet supported" % service_name)
                    continue

                print("- Creating component %s - %s" % (component, service_name))

                # todo Add support for binary_sensor
                if component == "sensor":
                    sensor = Sensor(service_name, service, device)
                    self.sensors.append(sensor)
                    self.components[sensor.unique_id] = sensor

                elif component == "light":
                    light = Light(service_name, service, device)
                    self.lights.append(light)
                    self.components[light.unique_id] = light

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

                        print("process ha: messages", messages)
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

