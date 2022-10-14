import json


def publish(mqtt):
    ''' Futurehome modus switch is stored as a sensor with the values
    home, away, sleep and vaction

    How to read mode switch (home, away, sleep, vacation)
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

    name = "Modus"
    value_template = \
        "{% if value_json.val.id == 'mode' %}{{ value_json.val.param.current }}" \
        "{% else %}{{states('sensor.fh_modus')}}{% endif %}"

    identifier = f"fh_modus"
    state_topic = "pt:j1/mt:evt/rt:app/rn:vinculum/ad:1"
    component = {
        "icon": "mdi:hexagon",
        "name": f"{name}",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "value_template": value_template,
    }

    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)
