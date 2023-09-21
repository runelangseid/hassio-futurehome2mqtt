"""
Creates sensors in Home Assistant based on FIMP services
"""
import json
import typing


def battery(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_battery"
    state_topic = f"pt:j1/mt:evt{service['addr']}"
    unit_of_measurement = "%"
    component = {
        "name": f"{name} (batteri)",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "device_class": "battery",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('batteryPercentage'):
        value = device['param']['batteryPercentage']
        data = {
            "props": {
                "unit": unit_of_measurement
            },
            "serv": "battery",
            "type": "evt.health.report",
            "val": value,
        }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status


def sensor_lumin(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_illuminance"
    state_topic = f"pt:j1/mt:evt{service['addr']}"
    unit_of_measurement = "lx"
    component = {
        "name": f"{name} (belysningsstyrke)",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "device_class": "illuminance",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('illuminance'):
        value = device['param']['illuminance']
        data = {
            "props": {
                "unit": unit_of_measurement
            },
            "serv": "sensor_lumin",
            "type": "evt.sensor.report",
            "val": value,
            "val_t": "float",
        }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status


def sensor_presence(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_sensor_presence"
    state_topic = f"pt:j1/mt:evt{service['addr']}"
    component = {
        "name": f"{name} (bevegelse)",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "device_class": "motion",
        "payload_off": False,
        "payload_on": True,
        "value_template": "{{ value_json.val }}",
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/binary_sensor/{identifier}/config", payload)

    # Queue statuses
    value = False
    if device.get("param") and device['param'].get('presence'):
        value = device['param']['presence']
    data = {
        "props": {},
        "serv": "sensor_presence",
        "type": "evt.presence.report",
        "val_t": "bool",
        "val": value
    }
    payload = json.dumps(data)
    status = (state_topic, payload)
    return status


def sensor_temp(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_temperature"
    state_topic = f"pt:j1/mt:evt{service['addr']}"
    unit_of_measurement = "°C"
    component = {
        "name": f"{name} (temperatur)",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "device_class": "temperature",
        "unit_of_measurement": unit_of_measurement,
        "value_template": "{{ value_json.val | round(0) }}"
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('temperature'):
        value = device['param']['temperature']
        data = {
            "props": {
                "unit": unit_of_measurement
            },
            "serv": "sensor_temp",
            "type": "evt.sensor.report",
            "val": value,
            "val_t": "float",
        }
        payload = json.dumps(data)
        status = (state_topic, payload)
    return status


def meter_elec(
        device: typing.Any,
        mqtt,
        service,
):
    address = device["fimp"]["address"]
    name = device["client"]["name"]
    # todo add room
    room = device["room"]

    identifier = f"fh_{address}_meter_elec"
    state_topic = f"pt:j1/mt:evt{service['addr']}"
    component = {
        "name": f"{name} (forbruk)",
        "object_id": identifier,
        "unique_id": identifier,
        "state_topic": state_topic,
        "device_class": "energy",
        "state_class": "total_increasing",
        "unit_of_measurement": "kWh",
        "value_template": "{{ value_json.val }}"
    }
    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)

    # Queue statuses
    status = None
    if device.get("param") and device['param'].get('energy'):
        value = device['param']['energy']
        data = {
            "props": {
                "unit": "kWh"
            },
            "serv": "meter_elec",
            "type": "evt.meter.report",
            "val": value,
        }

        payload = json.dumps(data)
        status = (state_topic, payload)
    return status
