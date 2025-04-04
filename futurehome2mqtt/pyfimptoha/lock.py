import json
import typing


def door_lock(
        mqtt,
        device: typing.Any,
        state_topic,
        identifier,
        default_component,
        command_topic
):
    """
    Creates lock in Home Assistant based on FIMP services
    """

    lock_component = {
        "command_topic": command_topic,
        "payload_lock": """
            {
                "props": {},
                "serv": "door_lock",
                "tags": [],
                "type": "cmd.lock.set",
                "val": true,
                "val_t": "bool",
                "src": "homeassistant"
            }
        """,
        "payload_unlock": """
            {
                "props": {},
                "serv": "door_lock",
                "tags": [],
                "type": "cmd.lock.set",
                "val": false,
                "val_t": "bool",
                "src": "homeassistant"
            }
        """,
        "value_template": '{{ iif(value_json.val["is_secured"], "LOCKED", "UNLOCKED", None) }}',
    }

    # Merge default_component with lock_component
    merged_component = {**default_component, **lock_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/lock/{identifier}/config", payload)

    # Queue status
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
            },
            "src": "homeassistant"
        }
        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
