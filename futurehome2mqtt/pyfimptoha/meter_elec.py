import json


def new_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    if "evt.meter_ext.report" in device["services"][service_name]["intf"]:
        meter_elec_ext_sensor(**locals())
    if "evt.meter.report" in device["services"][service_name]["intf"]:
        return meter_elec_sensor(**locals())
    return


def meter_elec_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    """
    Creates meter_elec sensors in Home Assistant based on FIMP services
    """

    sup_units: list = device["services"][service_name]["props"]["sup_units"]
    identifier_for_unit = identifier
    statuses = []

    for unit in sup_units:
        identifier = f"{identifier_for_unit}_{unit}"
        value_template = f"""
            {{% if value_json.props.unit == "{unit}" %}}
                {{{{ value_json.val | round(1) }}}}
            {{% endif %}}
        """

        if unit == "kWh":
            create_sensor("(energi)", "energy", "total_increasing", "kWh", value_template, identifier, default_component, mqtt)

            # Queue statuses
            payload = queue_status(
                param="energy",
                device=device,
                props={"unit": "kWh"},
                serv="meter_elec",
                typ="evt.meter.report",
                val_t="float"
            )
            if payload:
                statuses.append((state_topic, payload))

        elif unit == "W":
            create_sensor("(forbruk)", "power", "measurement", "W", value_template, identifier, default_component, mqtt)

            # Queue statuses
            payload = queue_status(
                param="wattage",
                device=device,
                props={"unit": "W"},
                serv="meter_elec",
                typ="evt.meter.report",
                val_t="float"
            )
            if payload:
                statuses.append((state_topic, payload))

        elif unit == "V":
            create_sensor("(volt)", "voltage", "measurement", "V", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report.

        elif unit == "A":
            create_sensor("(amp)", "current", "measurement", "A", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report.

    return statuses


def queue_status(param, device, props, serv, typ, val_t):
    payload = None
    if device.get("param") and device["param"].get(f"{param}"):
        value = device["param"][f"{param}"]
        data = {
            "props": props,
            "serv": f"{serv}",
            "type": f"{typ}",
            "val": float(value),
            "val_t": val_t,
            "src": "homeassistant"
        }

        payload = json.dumps(data)
    return payload


def meter_elec_ext_sensor(
        mqtt,
        device,
        service_name,
        state_topic,
        identifier,
        default_component
):
    """
    Creates meter_ext sensors in Home Assistant based on FIMP services
    """

    # Create extended meter_elec sensors
    sup_extended_vals: list = device["services"][service_name]["props"]["sup_extended_vals"]
    identifier_for_ext_vals = identifier
    for ext_val in sup_extended_vals:
        identifier = f"{identifier_for_ext_vals}_{ext_val}"
        value_template = f"""
            {{% if value_json.type == "evt.meter_ext.report" and value_json.val.{ext_val} is defined %}}
                {{{{ value_json.val.{ext_val} | round(1) }}}}
            {{% endif %}}
        """

        if ext_val in ["u1", "u2", "u3"]:
            create_sensor(ext_val, "voltage", "measurement", "V", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report

        elif ext_val in ["i1", "i2", "i3"]:
            create_sensor(ext_val, "current", "measurement", "A", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report

        elif ext_val in ["p_import"]:
            create_sensor(ext_val, "power", "measurement", "W", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report

        elif ext_val in ["e_import"]:
            create_sensor(ext_val, "energy", "total_increasing", "kWh", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report

        elif ext_val in ["p_import_react", "p_export_react"]:
            create_sensor(ext_val, "reactive_power", "measurement", "var", value_template, identifier, default_component, mqtt)

            # Queue statuses
            # TODO: Status will be 'unknown' until first report


def create_sensor(name, device_class, state_class, unit_of_measurement, value_template, identifier, default_component, mqtt):
    x_component = {
        "name": f"{name}",
        "device_class": device_class,
        "state_class": state_class,
        "unit_of_measurement": unit_of_measurement,
        "value_template": value_template,
        "object_id": identifier,
        "unique_id": identifier
    }
    merged_component = {**default_component, **x_component}
    payload = json.dumps(merged_component)
    mqtt.publish(f"homeassistant/sensor/{identifier}/config", payload)
