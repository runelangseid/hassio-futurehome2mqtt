import json
import time
import paho.mqtt.client as client
import pyfimptoha.sensor as sensor
import pyfimptoha.light as light
import pyfimptoha.lock as lock


def create_components(
    devices: list,
    selected_devices: list,
    mqtt: client,
):
    """
    Creates HA components out of FIMP devices
    by pushing them to HA using mqtt discovery
    """

    print('Received list of devices from FIMP. FIMP reported %s devices' % (len(devices)))
    print('Devices without rooms are ignored')

    statuses = []

    for device in devices:
        address = device["fimp"]["address"]
        name = device["client"]["name"]
        functionality = device["functionality"]
        room = device["room"]

        # Skip device without room
        if device["room"] is None:
            continue

        # When debugging: Ignore everything except selected_devices if set
        if selected_devices and address not in selected_devices:
            print(f"Skipping: {address} {name}")
            continue

        print(f"Creating: {address} {name}")
        print(f"- Functionality: {functionality}")

        for service_name, service in device["services"].items():
            # Adding sensors
            # todo add more sensors: alarm_power?, sensor_power. see old sensor.py
            status = None
            if service_name == "battery":
                print(f"- Service: {service_name}")
                status = sensor.battery(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
            elif service_name == "meter_elec":
                status = sensor.meter_elec(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
            elif service_name == "sensor_lumin":
                print(f"- Service: {service_name}")
                status = sensor.sensor_lumin(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
            elif service_name == "sensor_presence":
                print(f"- Service: {service_name}")
                status = sensor.sensor_presence(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
            elif service_name == "sensor_temp":
                print(f"- Service: {service_name}")
                status = sensor.sensor_temp(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
            if status:
                statuses.append(status)

            # Door lock
            elif service_name == "door_lock":
                print(f"- Service: {service_name}")
                status = lock.door_lock(
                    device=device,
                    mqtt=mqtt,
                    service=service,
                )
                if status:
                    statuses.append(status)

            # Lights
            elif functionality == "lighting":
                status = None
                if service_name == "out_lvl_switch":
                    print(f"- Service: {service_name}")
                    status = light.out_lvl_switch(
                        service_name=service_name,
                        device=device,
                        mqtt=mqtt,
                        service=service,
                    )
                elif service_name == "out_bin_switch":
                    status = light.out_bin_switch(
                        service_name=service_name,
                        device=device,
                        mqtt=mqtt,
                        service=service,
                    )

                if status:
                    statuses.append(status)

            # Appliance
            elif functionality == "appliance":
                # Binary switch
                if service_name == "out_bin_switch":
                    identifier = f"fh_{address}_{service_name}"
                    command_topic = f"pt:j1/mt:cmd{service['addr']}"
                    state_topic   = f"pt:j1/mt:evt{service['addr']}"
                    component = {
                        "name": f"{device['client']['name']}",
                        "object_id": identifier,
                        "unique_id": identifier,
                        "device_class": "outlet",
                        "schema": "template",
                        "command_topic": command_topic,
                        "state_topic": state_topic,
                        "payload_on":  '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":true,"val_t":"bool"}',
                        "payload_off": '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":false,"val_t":"bool"}',
                        "value_template": '{{ value_json.val }}',
                        "state_on": True,
                        "state_off": False,
                    }
                    payload = json.dumps(component)
                    mqtt.publish(f"homeassistant/switch/{identifier}/config", payload)

                    # Push statuses
                    if device.get("param") and device['param'].get('power'):
                        power = device['param']['power']
                        data = {
                            "props": {},
                            "serv": "out_bin_switch",
                            "type": "cmd.binary.report",
                            "val_t": "bool",
                            "val": True if power == 'on' else False
                        }
                        payload = json.dumps(data)
                        statuses.append((state_topic, payload))

                pass

    mqtt.loop()
    time.sleep(2)
    print("Publishing statuses...")
    for state in statuses:
        topic = state[0]
        payload = state[1]
        mqtt.publish(topic, payload)
        print(topic)
    print("Finished pushing statuses...")
