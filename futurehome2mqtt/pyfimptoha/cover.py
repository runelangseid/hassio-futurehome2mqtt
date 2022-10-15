"""
Creates covers in Home Assistant based on FIMP services
"""
import json
import typing


def blind(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_blind"
    command_topic = f"pt:j1/mt:cmd{service['addr']}"

    payload_close = """
        {
            "props":{},
            "serv":"out_lvl_switch",
            "tags":[],
            "type":"cmd.lvl.set",
            "val_t":"int",
            "ver":"1",
            "val": 0
        }
    """

    state_topic = f"pt:j1/mt:evt{service['addr']}"
    set_position_topic = f"pt:j1/mt:cmd{service['addr']}"
    component = {
        "name": f"{name} (persienne)",
        "object_id": identifier,
        "unique_id": identifier,
        "command_topic": command_topic,
        "payload_close": payload_close,
        "payload_open": payload_close.replace('"ver":"1"', '"ver":"100"'),
        "set_position_topic": set_position_topic,
        "set_position_template": """
            {
                "props":{
                },
                "serv":"out_lvl_switch",
                "tags":[],
                "type":"cmd.lvl.set",
                "val_t":"int",
                "ver":"1",
                "val": {{ position }}
            }
        """,
        # read position
        "position_topic": state_topic,
        "position_template": "{{ value_json.val | round(0) }}",
        "state_topic": "home-assistant/cover/state",
        "value_template": "valuee {{ value_json.val | round(0) }}"
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/cover/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and isinstance(device['param'].get('position'), int):
        value = device['param']['position']
        data = {
            "props": {},
            "serv": "out_lvl_switch",
            "type": "evt.lvl.report",
            "val": value,
        }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
