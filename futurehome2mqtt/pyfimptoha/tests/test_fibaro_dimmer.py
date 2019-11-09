import pytest
import json
import pyfimptoha.client as fimp

"""
Senors:
- device_class
 - None
 - battery
 - humidity
 - illuminance
 - signal_strength
 - temperature          (°C or °F)
 - power                (W or kW)
 - pressure
 - timestamp
"""


class TestFibaroDimmer:
    def test_fibaro_dimmer_2(self):
        f = fimp.Client()
        f.load_json_device("discovery_fibaro_dimmer_2.json")
        discovery = f.get_discovery_mqtt()
        expected = list()

        # Device: out_lvl_switch (Dimmer switch)
        # - Light does not need 'device_class'
        topic = "homeassistant/light/7-out_lvl_switch/config"
        payload = {
            "name": "Fibaro - Dimmer 2 - FGD-212  (ch1) - Light with dimmer (out_lvl_switch)",
            "state_topic": topic.replace("config", "state"),
            "command_topic": topic.replace("config", "set"),
            "brightness_scale": 100,
            "brightness_state_topic": topic.replace("config", "state"),
            "brightness_command_topic": topic.replace("config", "command"),
            "payload_on": True,
            "payload_off": False,
        }
        device = {
            "topic": topic,
            "payload": json.dumps(payload),
        }
        expected.append(device)

        # Device: sensor_power (Power sensor)
        topic = "homeassistant/sensor/7-sensor_power/config"
        payload = {
            "name": "Fibaro - Dimmer 2 - FGD-212  (ch1) - Light with dimmer (sensor_power)",
            "state_topic": topic.replace("config", "state"),
            "unit_of_measurement": "W",
        }
        device = {
            "topic": topic,
            "payload": json.dumps(payload),
        }
        expected.append(device)

        # print("expected", expected)
        # print("discovered", discovery)

        assert discovery == expected
