import json
from pyfimptoha.base import Base

class Sensor(Base):
    '''Implementation of MQTT sensor
    https://www.home-assistant.io/integrations/sensor.mqtt

    Device class:
    https://www.home-assistant.io/integrations/sensor/#device-class
        None                Supported
        battery             Supported
        humidity            Unsupported
        illuminance         Supported
        signal_strength     Unsupported
        temperature         Supported
        power               Supported
        pressure            Unsupported
        timestamp           Unsupported
        presence            Unsupported
    '''

    _device_class = None
    _expire_after = 0
    _icon = None
    _name_prefix = ""
    _unit_of_measurement = None
    _value_template = None

    _init_value = None

    def __init__(self, service_name, service, device):
        '''
        Example
        service_name:   sensor_power
        service (json): {'addr': '/rt:dev/rn:zw/ad:1/sv:sensor_power/ad:41_0' ...
        device (json):  {'client': {'name': 'Ovn (gang)'}, 'fimp': {'adapter': 'zwave-ad', ...
        '''
        super().__init__(service_name, service, device, "sensor")
        self._name = self.name_prefix + self._name

        # todo Move _value_template to set_type(). round(0) it probably not a good idea
        self._value_template = "{{ value_json.val | round(0) }}"

        self.set_type()

    @staticmethod
    def supported_services():
        sensors = [
            'battery',
            'scene_ctrl',
            'sensor_lumin',
            'sensor_power',
            'sensor_temp',
            'sensor_precence',
            'sensor_temp',
        ]
        return sensors

    @property
    def icon(self):
        '''Return the icon of the sensor.'''
        return "mdi:" + self._icon

    @property
    def unit_of_measurement(self):
        '''Return the unit_of_measurement of the sensor.'''
        return self._unit_of_measurement

    @property
    def name_prefix(self):
        '''Return the name prefix for this sensor.'''
        return self._name_prefix

    def set_type(self):
        '''
        Set various properties like name prefix and
        device class based on "service_name"
        '''

        device_class = None
        prefix = ""
        unit_of_measurement = ""

        if self._service_name == "battery":
            device_class = "battery"
            prefix = "Batteri: "
            unit_of_measurement = "%"

            if 'batteryPercentage' in self._device['param']:
                self._init_value = self._device['param']['batteryPercentage']
        elif self._service_name == "sensor_lumin":
            device_class = "illuminance"
            prefix = "Belysningsstyrke: "
            unit_of_measurement = "Lux"
            self._icon = "mdi:ceiling-light"

            if 'illuminance' in self._device['param']:
                self._init_value = self._device['param']['illuminance']
        elif self._service_name == "sensor_power":
            device_class = "power"
            prefix = "Forbuk: "
            unit_of_measurement = "Watt"

            if 'wattage' in self._device['param']:
                self._init_value = self._device['param']['wattage']
        elif self._service_name  == "sensor_temp":
            device_class = "temperature"
            prefix = "Temperatur: "
            unit_of_measurement = "°C"

            if 'temperature' in self._device['param']:
                self._init_value = self._device['param']['temperature']
        elif self._service_name  == "scene_ctrl":
            prefix = "Scene: "
            self._value_template = "{{ value_json.val }}"
            self._expire_after = 1


        self._device_class = device_class
        self._name_prefix = prefix
        self._unit_of_measurement = unit_of_measurement

    def get_component(self):
        '''Returns MQTT component to HA'''

        payload = {
            "name": self._name,
            "state_topic": self._state_topic,
            "unit_of_measurement": self.unit_of_measurement,
            "unique_id": self.unique_id,
            "value_template": self._value_template,
        }

        if self._device_class:
            payload["device_class"] = self._device_class

        if self._expire_after:
            payload["expire_after"] = self._expire_after

        if self._icon:
            payload["icon"] = self.icon

        device = {
            "topic": self._config_topic,
            "payload": json.dumps(payload),
        }

        return device

    def get_init_state(self):
        '''Return the initial state of the sensor'''
        payload = {"val": self._init_value}
        data = [
            {"topic": self._state_topic, "payload": json.dumps(payload)},
        ]

        return data
