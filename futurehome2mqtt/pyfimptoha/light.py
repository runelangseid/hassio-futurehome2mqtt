import json
import typing


def new_light(
        mqtt,
        device: typing.Any,
        service_name: str,
        state_topic,
        identifier,
        default_component,
        command_topic
):
    """
    Creates light in Home Assistant based on FIMP services
    """

    light_component = {
        "command_topic": command_topic,
        "schema": "template",
        "state_template": "{% if value_json.val %} on {% else %} off {% endif %}"
    }

    out_lvl_switch_spesific = {
        "brightness_scale": 100,
        "command_on_template": """
                {
                    "props":{},
                    "src":"homeassistant",
                    "serv":"out_lvl_switch",
                    "tags":[]
                {%- if brightness is defined -%}
                    , "type":"cmd.lvl.set",
                    "val":{{ (brightness / 2.55) | int }},
                    "val_t":"int"
                {%- else -%}
                    , "type":"cmd.binary.set",
                    "val":true,
                    "val_t":"bool"
                {%- endif -%}
                }
            """,
        "command_off_template": """
                {
                    "props":{},
                    "src":"homeassistant",
                    "serv":"out_lvl_switch",
                    "tags":[],
                    "type":"cmd.binary.set",
                    "val":false,
                    "val_t":"bool"
                }
            """,
        "brightness_template": "{{ (value_json.val * 2.55) | int }}"
    }

    out_bin_switch_spesific = {
        "payload_on": '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":true,"val_t":"bool","src":"homeassistant"}',
        "payload_off": '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":false,"val_t":"bool","src":"homeassistant"}',
        "command_on_template": """
            {
                "props":{},
                "serv":"out_bin_switch",
                "tags":[],
                "type":"cmd.binary.set",
                "val":true,
                "val_t":"bool",
                "src":"homeassistant"
            }
        """,
        "command_off_template": """
            {
                "props":{},
                "serv":"out_bin_switch",
                "tags":[],
                "type":"cmd.binary.set",
                "val":false,
                "val_t":"bool",
                "src":"homeassistant"
            }
        """
    }

    # Merge default_component with light_component
    extended_component = {**default_component, **light_component}
    if service_name == "out_lvl_switch":
        # merge extended_component and out_lvl_switch_spesific dicts
        merged_component = {**extended_component, **out_lvl_switch_spesific}
    elif service_name == "out_bin_switch":
        # merge extended_component and out_bin_switch_spesific dicts
        merged_component = {**extended_component, **out_bin_switch_spesific}
    else:
        print("An error occured while constructing device")

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/light/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('power'):
        power = device['param']['power']
        if power == "off" or service_name == "out_bin_switch":
            data = {
                "props": {},
                "serv": f"{service_name}",
                "type": "evt.binary.report",
                "val_t": "bool",
                "val": True if power == 'on' else False,
                "src": "homeassistant"
            }
        else:
            dim_value = device['param']['dimValue']
            data = {
                "props": {},
                "serv": "out_lvl_switch",
                "type": "evt.lvl.report",
                "val_t": "int",
                "val": dim_value,
                "src": "homeassistant"
            }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
