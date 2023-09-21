"""
Creates lock in Home Assistant based on FIMP services
"""

import json
import typing


def door_lock(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]

    identifier = f"fh_{address}_door_lock"
    command_topic = f"pt:j1/mt:cmd{service['addr']}"
    state_topic   = f"pt:j1/mt:evt{service['addr']}"
    component = {
        "name": f"{device['client']['name']}",
        "object_id": identifier,
        "unique_id": identifier,
        "command_topic": command_topic,
        "state_topic": state_topic,
        "payload_lock": '{"props":{},"serv":"door_lock","tags":[],"type":"cmd.lock.set","val":true,"val_t":"bool"}',
        "payload_unlock": '{"props":{},"serv":"door_lock","tags":[],"type":"cmd.lock.set","val":false,"val_t":"bool"}',
        "value_template": '{{ iif(value_json.val["is_secured"], "LOCKED", "UNLOCKED", None) }}',
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/lock/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('lockState'):
        lockState = device['param']['lockState']
        data = {
            "props": {},
            "serv": "door_lock",
            "type": "evt.lock.report",
            "val_t": "bool_map",
            "val": {
                "is_secured": True if lockState == 'locked' else False,
            }
        }
        payload = json.dumps(data)
        status = (state_topic, payload)
    return status