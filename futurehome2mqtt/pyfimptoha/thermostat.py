import json
import typing

def new_thermostat(
        mqtt,
        device: typing.Any,
        state_topic,
        identifier,
        default_component,
        command_topic,
        devices
):
    """
    Creates thermostat in Home Assistant based on FIMP services
    """

    statuses = []
    supported_thermostat_modes = [mode for mode in device["param"]["supportedThermostatModes"]]

    fan_component = new_fan_component(device)
    humid_component = new_humid_component(device)
    current_temperature_component = new_current_temperature_component(device, devices)

    thermostat_component = {
        "max_temp": 40.0,
        "min_temp": 5.0,
        "mode_command_template": """
            {
                "serv": "thermostat",
                "type": "cmd.mode.set",
                "val_t": "string",
                "val": "{{ value }}",
                "props": {},
                "tags": [],
                "src": "homeassistant"
            }
        """,
        "mode_command_topic": command_topic,
        "mode_state_template": f"""
            {{% if value_json.type == 'evt.mode.report' %}}
                {{{{ value_json.val }}}}
            {{% else %}}
                {{{{ states('climate.{identifier}') }}}}
            {{% endif %}}
        """,
        "mode_state_topic": state_topic,
        "modes": supported_thermostat_modes,
        "name": None,
        "temperature_command_template": """
            {
                "serv": "thermostat",
                "type": "cmd.setpoint.set",
                "val_t": "str_map",
                "val": {
                    "temp": "{{ value }}",
                    "type": "heat",
                    "unit": "C"
                },
                "props": {},
                "tags": [],
                "src": "homeassistant"
            }
        """,
        "temperature_command_topic": command_topic,
        "temperature_state_template": """
            {% if value_json.type == 'evt.setpoint.report' %}
                {{ value_json.val.temp }}
            {% endif %}
        """,
        "temperature_state_topic": state_topic,
        "temperature_unit": "C",
        "temp_step": 1.0 # default 1.0
    }

    # Merge default_component with thermostat_component
    merged_component = {**default_component, **thermostat_component}

    if fan_component:
        merged_component = {**merged_component, **fan_component}

    if humid_component:
        merged_component = {**merged_component, **humid_component}

    if current_temperature_component:
        merged_component = {**merged_component, **current_temperature_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/climate/{identifier}/config", payload)

    # Queue status
    if fan_component:
        fan_payload = {
            "props": {},
            "serv": "fan_ctrl",
            "type": "cmd.mode.get_report",
            "val_t": "string",
            "val": "",
            "src": "homeassistant"
        }
        fan_mode_payload = json.dumps(fan_payload)
        statuses.append((f"pt:j1/mt:cmd{device['services']['fan_ctrl']['addr']}", fan_mode_payload))

    if device.get("param") and device["param"].get("targetTemperature"):
        temp = device["param"]["targetTemperature"]
        data_temp = {
            "props": {},
            "serv": "thermostat",
            "type": "evt.setpoint.report",
            "val_t": "str_map",
            "val": {
                "temp": f"{temp}",
                "type": "heat",
                "unit": "C"
            },
            "src": "homeassistant"
        }
        payload_temp = json.dumps(data_temp)
        if payload_temp:
            statuses.append((state_topic, payload_temp))

    if device.get("param") and device["param"].get("thermostatMode"):
        mode = device["param"]["thermostatMode"]
        data_mode = {
            "props": {},
            "serv": "thermostat",
            "type": "evt.mode.report",
            "val_t": "string",
            "val": f"{mode}",
            "src": "homeassistant"
        }
        payload_mode = json.dumps(data_mode)
        if payload_mode:
            statuses.append((state_topic, payload_mode))
    return statuses


def new_fan_component(device):
    if "fan_ctrl" not in device["services"]:
        return

    fan_ctrl = device["services"]["fan_ctrl"]
    supported_fan_modes = [mode for mode in fan_ctrl["props"]["sup_modes"]]
    fan_component = {
        "fan_mode_command_template": """
            {
                "serv": "fan_ctrl",
                "type": "cmd.mode.set",
                "val_t": "string",
                "val": "{{ value }}",
                "props": {},
                "tags": [],
                "src": "homeassistant"
            }
        """,
        "fan_mode_command_topic": f"pt:j1/mt:cmd{fan_ctrl['addr']}",
        "fan_mode_state_template": """
            {% if value_json.type == 'evt.mode.report' %}
                {{ value_json.val }}
            {% endif %}
        """,
        "fan_mode_state_topic": f"pt:j1/mt:evt{fan_ctrl['addr']}",
        "fan_modes": supported_fan_modes
    }
    return fan_component


def new_humid_component(device):
    if "sensor_humid" not in device["services"]:
        return

    sensor_humid = device["services"]["sensor_humid"]
    humid_component = {
        "current_humidity_template": """
            {% if value_json.type == 'evt.sensor.report' %}
                {{ value_json.val | round(0) }}
            {% endif %}
        """,
        "current_humidity_topic": f"pt:j1/mt:evt{sensor_humid['addr']}"
    }
    return humid_component


def new_current_temperature_component(device, devices):
    topic = None
    current_temperature_component = None

    if "sensor_temp" in device["services"]:
        topic = f"pt:j1/mt:evt{device['services']['sensor_temp']['addr']}"
    else:
        # Handling when current_temp sensor is not on the same device (channel)
        # (e.g Heatit floor sensor on _4 or room sensor on _3)
        thing_id = device["thing"]
        for dev in devices:
            if dev["thing"] == thing_id:
                topic = [f"pt:j1/mt:evt{service['addr']}" for service_name, service in dev["services"].items() \
                    if service["props"].get("thing_role") and service["props"]["thing_role"] == "main"]
                if topic:
                    topic = topic[0]
                    break

    if topic:
        current_temperature_component = {
            "current_temperature_topic": topic,
            "current_temperature_template": """
                {% if value_json.type == 'evt.sensor.report' %}
                    {{ value_json.val | round(1) }}
                {% endif %}
            """
        }
    return current_temperature_component
