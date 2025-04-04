import json


def create(mqtt, mode):
    """
    Creates select in Home Assistant based on FIMP mode
    """

    identifier = "fh_mode"
    command_topic = "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
    state_topic = "pt:j1/mt:evt/rt:app/rn:vinculum/ad:1"
    component = {
        "icon": "mdi:hexagon",
        "name": "Modus",
        "object_id": identifier,
        "unique_id": identifier,
        "device": {
            "identifiers": "futurehome_smarthub",
            "name": "Futurehome Smarthub",
            "suggested_area": "Futurehome Smarthub",
            "manufacturer": "Futurehome"
        },
        "command_topic": command_topic,
        "state_topic": state_topic,
        "value_template": """
            {% if value_json.val.id == 'mode' %}
                {{ value_json.val.param.current }}
            {% endif %}
        """,
        "options": ["home", "away", "sleep", "vacation"],
        "command_template": """
            {
                "serv": "vinculum",
                "type": "cmd.pd7.request",
                "val_t": "object",
                "val": {
                    "cmd": "set",
                    "component": "mode",
                    "id": "{{ value }}",
                    "client": null,
                    "param": null,
                    "requestId": null
                    },
                "props": {},
                "tags": null,
                "src": "homeassistant",
                "ver": "1",
                "resp_to": "pt:j1/mt:rsp/rt:app/rn:homeassistant-client/ad:1",
                "topic": "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
            }
            """
    }

    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/select/{identifier}/config", payload)

    # Queue status
    status = None
    if mode:
        data = {
            "props": {},
            "serv": "vinculum",
            "type": "evt.pd7.notify",
            "val_t": "object",
            "val": {
                "cmd": "set",
                "component": "hub",
                "id": "mode",
                "param": {
                    "current": mode
                }
            },
            "src": "homeassistant"
        }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
