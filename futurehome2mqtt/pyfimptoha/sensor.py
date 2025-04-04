import json
import typing


def new_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    """
    Creates sensors in Home Assistant based on FIMP services
    """

    if service_name == "battery":
        return battery(**locals())

    elif service_name == "sensor_lumin":
        return sensor_lumin(**locals())

    elif service_name == "sensor_presence":
        return sensor_presence(**locals())

    elif service_name == "sensor_temp":
        return sensor_temp(**locals())

    elif service_name == "sensor_humid":
        return sensor_humid(**locals())

    elif service_name == "sensor_contact":
        return sensor_contact(**locals())

    else:
        print("Failed to create sensor")
        return


def battery(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    unit_of_measurement = "%"
    battery_component = {
        "name": "(batteri)",
        "device_class": "battery",
        # "entity_category": "diagnostic",
        "unit_of_measurement": unit_of_measurement,
        "value_template": """
            {% if value_json.type == 'evt.lvl.report' %}
                {{ value_json.val | round(0) }}
            {% endif %}
        """
    }

    # Merge default_component with battery_component
    merged_component = {**default_component, **battery_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="batteryPercentage",
        device=device,
        props={},
        serv="battery",
        typ="evt.lvl.report",
        val_t="int"
    )
    if payload:
        status = (state_topic, payload)
    return status

# TODO add binary_sensor for evt.alarm.report for low_battery event as recursive function
# https://futurehomeno.github.io/fimp-api/#/device_services/generic/battery?id=definitions


def sensor_lumin(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    unit_of_measurement = "lx"
    lumin_component = {
        "name": "(belysningsstyrke)",
        "device_class": "illuminance",
        "unit_of_measurement": unit_of_measurement,
        "value_template": """
            {% if value_json.type == 'evt.sensor.report' %}
                {{ value_json.val | round(0) }}
            {% endif %}
        """
    }

    # Merge default_component with lumin_component
    merged_component = {**default_component, **lumin_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="illuminance",
        device=device,
        props={"unit": "Lux"},
        serv="sensor_lumin",
        typ="evt.sensor.report",
        val_t="float"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_presence(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    presence_component = {
        "name": "(bevegelse)",
        "device_class": "motion",
        "payload_off": False,
        "payload_on": True,
        "value_template": """
            {% if value_json.type == 'evt.presence.report' %}
                {{ value_json.val }}
            {% endif %}
        """
    }

    # Merge default_component with presence_component
    merged_component = {**default_component, **presence_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/binary_sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="presence",
        device=device,
        props={},
        serv="sensor_presence",
        typ="evt.presence.report",
        val_t="bool"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_temp(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):

    unit_of_measurement = "°C"
    temp_component = {
        "name": "(temperatur)",
        "device_class": "temperature",
        "unit_of_measurement": unit_of_measurement,
        "value_template": """
            {% if value_json.type == 'evt.sensor.report' %}
                {{ value_json.val | round(1) }}
            {% endif %}
        """
    }

    # This will prevent device name for Heatit z-trm3 to be overwritten with the sensor name
    del default_component["device"]["name"]

    # Merge default_component with temp_component
    merged_component = {**default_component, **temp_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="temperature",
        device=device,
        props={"unit": "C"},
        serv="sensor_temp",
        typ="evt.sensor.report",
        val_t="float"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_humid(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    unit_of_measurement = "%"
    humid_component = {
        "name": "(luftfuktighet)",
        "device_class": "humidity",
        "unit_of_measurement": unit_of_measurement,
        "value_template": """
            {% if value_json.type == 'evt.sensor.report' %}
                {{ value_json.val | round(0) }}
            {% endif %}
        """
    }

    # Merge default_compontent with humid_component
    merged_component = {**default_component, **humid_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="humidity",
        device=device,
        props={"unit": unit_of_measurement},
        serv="sensor_humid",
        typ="evt.sensor.report",
        val_t="string"
    )
    if payload:
        status = (state_topic, payload)
    return status


def sensor_contact(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    # FH supports: door, window, lock, garage, door_lock, window_lock, other
    fh_subtype = device["type"]["subtype"] if device.get("type") and device["type"].get("subtype") else None
    supported_sensor_subtypes = ["door", "window", "garage"]

    device_class = fh_subtype if fh_subtype in supported_sensor_subtypes else None
    if device_class == "garage":
        device_class = "garage_door"

    contact_component = {
        "name": "(kontaktsensor)",
        "device_class": device_class,
        "payload_off": False,
        "payload_on": True,
        "value_template": """
            {% if value_json.type == 'evt.open.report' %}
                {{ value_json.val }}
            {% endif %}
        """
    }

    # Merge default_component with presence_component
    merged_component = {**default_component, **contact_component}

    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/binary_sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    payload = queue_status(
        param="openState",
        device=device,
        props={},
        serv="sensor_contact",
        typ="evt.open.report",
        val_t="bool",
    )
    if payload:
        payload_dict = json.loads(payload)
        payload_dict["val"] = True if payload_dict["val"] == "open" else False
        payload = json.dumps(payload_dict)
        status = (state_topic, payload)
    return status


def queue_status(param, device, props, serv, typ, val_t):
    payload = None
    if device.get("param") and device["param"].get(f"{param}"):
        value = device["param"][f"{param}"]
        data = {
            "props": props,
            "serv": f"{serv}",
            "type": f"{typ}",
            "val": value,
            "val_t": val_t,
            "src": "homeassistant"
        }

        payload = json.dumps(data)
    return payload
