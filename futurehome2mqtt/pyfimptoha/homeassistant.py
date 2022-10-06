import json
import time
import paho.mqtt.client as client


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

    # todo Add support for Wall plugs with functionality 'Lighting'

    for device in devices:
        address = device["fimp"]["address"]
        name = device["client"]["name"]
        functionality = device["functionality"]
        room = device["room"]

        # Skip device without room
        if device["room"] is None:
            # self.log('Skipping: %s %s' % (address, name))
            continue

        #  When debugging: Ignore everything except self._selected_devices if set
        if selected_devices and address not in selected_devices:
            print('Skipping: %s %s' % (address, name))
            continue

        print("Creating: %s %s" % (address, name))
        print("- Functionality: %s" % (functionality))

        # if address != '21':
        #   continue

        for service_name in device["services"]:
            # Service meter_elec - "Forbruk"
            if service_name == "meter_elec":
                identifier = f"fh_{address}_meter_elec"
                state_topic = f"pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:meter_elec/ad:{address}_0"
                component = {
                    "name": f"{device['client']['name']} (forbruk)",
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
                    statuses.append((state_topic, payload))

            # Lights
            elif functionality == "lighting":
                if service_name == "out_lvl_switch":
                    identifier = f"fh_{address}_{service_name}"
                    command_topic = f"pt:j1/mt:cmd/rt:dev/rn:zw/ad:1/sv:out_lvl_switch/ad:{address}_1"
                    state_topic = f"pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_lvl_switch/ad:{address}_1"
                    component = {
                        "name": f"{device['client']['name']}",
                        "object_id": identifier,
                        "unique_id": identifier,
                        "schema": "template",
                        "command_topic": command_topic,
                        "state_topic": state_topic,
                        "brightness_scale": 100,
                        "command_on_template": """
                            {
                              "props":{},
                              "serv":"out_lvl_switch",
                              "tags":[]
                            {%- if brightness -%}
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
                            {"props":{},
                              "serv":"out_lvl_switch",
                              "tags":[],
                              "type":"cmd.binary.set",
                              "val":false,
                              "val_t":"bool"}
                        """,
                        "state_template": "{% if value_json.val %} on {% else %} off {% endif %}",
                        "brightness_template": "{% if value_json.val_t %}{{ (value_json.val * 2.55) | int }}{% endif %}"
                    }
                    payload = json.dumps(component)
                    mqtt.publish(f"homeassistant/light/{identifier}/config", payload)

                    # Queue statuses
                    if device.get("param") and device['param'].get('power'):
                        power = device['param']['power']
                        if power == "off":
                            data = {
                                "props": {},
                                "serv": "out_lvl_switch",
                                "type": "cmd.binary.report",
                                "val_t": "bool",
                                "val": False
                            }
                        else:
                            dim_value = device['param']['dimValue']
                            data = {
                                "props": {},
                                "serv": "out_lvl_switch",
                                "type": "cmd.lvl.report",
                                "val_t": "int",
                                "val": dim_value
                            }
                        payload = json.dumps(data)
                        statuses.append((state_topic, payload))

            # todo Add support for binary_sensor?

    mqtt.loop()
    time.sleep(2)
    print("Publishing statuses...")
    for state in statuses:
        topic = state[0]
        payload = state[1]
        mqtt.publish(topic, payload)
        print(topic)
    print("Finished pushing statuses...")
