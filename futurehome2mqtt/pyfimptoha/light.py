import json

class Light:
    """Implementation of MQTT light
    https://www.home-assistant.io/integrations/light.mqtt
    """

    _name = ""
    _address = None
    _room = ""
    _service_name = None
    _unique_id = None

    _config_topic = None
    _command_topic = None

    # todo Add support for more properties
    _state_value = False
    _brightness_value = None

    _brightness_scale = 100
    _brightness_state_topic = None
    _brightness_command_topic = None

    topics = list()

    _payload_on: True
    _payload_off: False

    # def __init__(self, address, name, room, service_name, service):
    def __init__(self, service_name, service, device):
        self._address = device["fimp"]["address"]
        self._device = device
        self._name = device["client"]["name"]
        self._room = device["room"]
        self._service = service
        self._service_name = service_name
        self._unique_id = self._address + "-" + service_name

        # topic: homeassistant/light/7_sensor_power/config
        self._config_topic = "homeassistant/light/%s/config" % (self._unique_id)
        self._state_topic = self._config_topic.replace("config", "state")
        self._command_topic = self._config_topic.replace("config", "set")
        self._brightness_state_topic = self._config_topic.replace(
            "config", "brightness_state"
        )
        self._brightness_command_topic = self._config_topic.replace(
            "config", "brightness_command"
        )

        # Set current values
        self._brightness_value = self._device["param"]["dimValue"]
        if self._device["param"]["power"] == "on":
            self._state_value = True

        if self._address != "7":
            return

    @property
    def unique_id(self):
        """Return the unique id of the light.
        """
        return self._unique_id

    def get_component(self):
        payload = {
            "name": self._name,
            "state_topic": self._state_topic,
            "command_topic": self._command_topic,
            "brightness_scale": 100,
            "brightness_state_topic": self._brightness_state_topic,
            "brightness_command_topic": self._brightness_command_topic,
            # "optimistic": True,
            "payload_on": True,
            "payload_off": False,
            "unique_id": self._unique_id,
        }

        device = {
            "topic": self._config_topic,
            "payload": json.dumps(payload),
        }

        return device

    def get_state(self):
        """ Return the current state of the light
        On/off and dim level
        """
        data = [
            {"topic": self._state_topic, "payload": self._state_value,},
            {"topic": self._brightness_state_topic, "payload": self._brightness_value},
        ]

        return data

    def handle_ha(self, topic_type, payload):
        """ Handle message from HA and send cmd to FIMP
        We also send a state message back to HA
        """
        # print(
        #     "Light received: %s.  State: %s. Payload: %s"
        #     % (self.unique_id, topic_type, payload)
        # )
        # print("Brightness value is", self._brightness_value)

        topic_fimp = "pt:j1/mt:cmd/rt:dev/rn:zw/ad:1/sv:%s/ad:%s_1" % (
            self._service_name,
            self._address,
        )

        if topic_type == "set":
            val = False

            if payload == "True":
                val = True

            if val == self._state_value:
                print("Light: Received current state. Skipping")
                return

            self._state_value = val

            # Send update to FIMP and status update to HA
            payload_fimp = {
                "props": {},
                "serv": self._service_name,
                "tags": [],
                "type": "cmd.binary.set",
                "val": val,
                "val_t": "bool",
            }

            data = [
                {"topic": self._state_topic, "payload": payload},
                {
                    "topic": self._brightness_state_topic,
                    "payload": self._brightness_value,
                },
                {"topic": topic_fimp, "payload": json.dumps(payload_fimp)},
            ]
            return data

        elif topic_type == "brightness_command":
            # print("Light: Received brightness_command")
            val = int(payload)
            self._brightness_value = val

            payload_fimp = {
                "props": {},
                "serv": self._service_name,
                "tags": [],
                "type": "cmd.lvl.set",
                "val": val,
                "val_t": "int",
            }
            data = [
                {"topic": topic_fimp, "payload": json.dumps(payload_fimp)},
            ]
            return data

    def handle_fimp(self, payload):
        # print('light.handle_fimp()', payload)
        topic = ''
        payload_out = None

        if payload['val_t'] == "bool":
            topic = self._state_topic
            payload_out = payload['val']
            # if payload['val'] == True:
            #     payload_out = True
            self._state_value = payload_out

        elif payload['val_t'] == "int":
            payload_out = payload['val']

            topic = self._brightness_state_topic
            self._brightness_value = payload_out

        data = [
            {
                "topic": topic,
                "payload": payload_out
            }
        ]

        return data
