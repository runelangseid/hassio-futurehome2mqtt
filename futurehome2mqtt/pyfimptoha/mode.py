import json

# todo re-implement
class Mode():
    '''Implementation of MQTT sensor
    https://www.home-assistant.io/integrations/sensor.mqtt

    Add Hub mode sensor (home, away, sleep, vacation)
    Topic: pt:j1/mt:evt/rt:app/rn:vinculum/ad:1

    {
    "ctime": "....",
    "serv": "vinculum",
    "val": {
        "component": "hub",
        "id": "mode",
        "param": {
        "current": "home",
        "prev": "home"
        }
    },
    "val_t": "object",
    "ver": "1"
    }
    '''

    _config_topic = None
    _name = None
    _state_topic = None
    _value_template = None

    def __init__(self):
        '''Create sensor `mode`.'''
        self._config_topic = "homeassistant/sensor/mode/config"
        self._name = "Modus"
        self._state_topic = "pt:j1/mt:evt/rt:app/rn:vinculum/ad:1"
        self._value_template = "{% if value_json.val.id == 'mode' %}{{ value_json.val.param.current }}{% else %}{{states('sensor.modus')}}{% endif %}"

    def get_component(self):
        '''Returns MQTT component to HA'''

        payload = {
            "icon": "mdi:hexagon",
            "name": self._name,
            "state_topic": self._state_topic,
            "unique_id": 'mode',
            "value_template": self._value_template,
        }

        device = {
            "topic": self._config_topic,
            "payload": json.dumps(payload),
        }

        return device
