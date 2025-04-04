"""
Creates switch in Home Assistant based on FIMP services
"""


import json
import typing


def new_switch(
        mqtt,
        device: typing.Any,
        state_topic,
        identifier,
        default_component,
        command_topic
):
    switch_component = {
        "device_class": "outlet",
        "command_topic": command_topic,
        "schema": "template",
        "payload_on":  """
            {
                "props": {},
                "serv": "out_bin_switch",
                "tags": [],
                "type": "cmd.binary.set",
                "val": true,
                "val_t": "bool",
                "src": "homeassistant"
            }
        """,
        "payload_off": """
            {
                "props": {},
                "serv": "out_bin_switch",
                "tags": [],
                "type": "cmd.binary.set",
                "val": false,
                "val_t": "bool",
                "src": "homeassistant"
            }
        """,
        "value_template": """
            {% if value_json.type == 'evt.binary.report' %}
                {{ value_json.val }}
            {% endif %}
        """,
        "state_on": True,
        "state_off": False
    }

    # Merge default_component with switch_component
    merged_component = {**default_component, **switch_component}
    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/switch/{identifier}/config", payload)

    # Queue status
    status = None
    if device.get("param") and device["param"].get("power"):
        power = device["param"]["power"]
        data = {
            "props": {},
            "serv": "out_bin_switch",
            "type": "evt.binary.report",
            "val_t": "bool",
            "val": True if power == "on" else False,
            "src": "homeassistant"
        }
        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
