import json
from pyfimptoha.base import Base

class Switch(Base):
    name_prefix = 'Switch: '
    init_power = False

    def __init__(self, service_name, service, device):
        super().__init__(service_name, service, device, "switch")
        self._name = self.name_prefix + self._name
        self._value_template = "{{ value_json.val }}"

        if device['param']['power'] == 'on':
            self.init_power = True

    def get_component(self):
        '''Returns MQTT component to HA'''
        '''
          - platform: mqtt
            name: "Wall plug (kontor)"
            state_topic:   "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_bin_switch/ad:34_0"
            command_topic: "pt:j1/mt:cmd/rt:dev/rn:zw/ad:1/sv:out_bin_switch/ad:34_0"
            value_template: '{{ value_json.val }}'
            payload_on:  '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":true,"val_t":"bool"}'
            payload_off: '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":false,"val_t":"bool"}'
            state_on: true
            state_off: false
        '''

        payload = {
            "name": self._name,
            "state_topic": self._state_topic,
            "command_topic": self._command_topic,
            "unique_id": self.unique_id,
            "value_template": self._value_template,
            "payload_on": '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":true,"val_t":"bool"}',
            "payload_off": '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":false,"val_t":"bool"}',
            "state_on": True,
            "state_off": False,
        }

        device = {
            "topic": self._config_topic,
            "payload": json.dumps(payload),
        }

        return device

    def get_init_state(self):
        '''Return the initial state of the switch'''
        data = [
            {"topic": self._state_topic, "payload": self.init_power},
        ]

        return data
