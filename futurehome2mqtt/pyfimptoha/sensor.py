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
    '''

    _device_class = None
    _icon = None
    _name_prefix = ""
    _unit_of_measurement = None
    _value_template = None

    def __init__(self, service_name, service, device):
        super().__init__(service_name, service, device)

        self._name = self.name_prefix + self._name
        self._state_topic = "pt:j1/mt:evt" + self._service['addr']

        # todo Move _value_template to set_type(). round(0) it probably not a good idea
        self._value_template = "{{ value_json.val | round(0) }}"

        self.set_type()

    @staticmethod
    def supported_services():
        sensors = [
            'battery',
            'sensor_lumin',
            'sensor_power',
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

        device_class = ""
        prefix = ""
        unit_of_measurement = ""

        if self._service_name == "battery":
            device_class = "battery"
            prefix = "Batteri: "
            unit_of_measurement = "%"
        elif self._service_name == "sensor_lumin":
            device_class = "illuminance"
            prefix = "Belysningsstyrke: "
            unit_of_measurement = "Lux"
            self._icon = "mdi:ceiling-light"
        elif self._service_name == "sensor_power":
            device_class = "power"
            prefix = "Forbuk: "
            unit_of_measurement = "Watt"
        elif self._service_name  == "sensor_temp":
            device_class = "temperature"
            prefix = "Temperatur: "
            unit_of_measurement = "°C"

        self._device_class = device_class
        self._name_prefix = prefix
        self._unit_of_measurement = unit_of_measurement

    def get_component(self):
        '''Returns MQTT component to HA'''

        payload = {
            "name": self._name,
            "device_class": self._device_class,
            "state_topic": self._state_topic,
            "unit_of_measurement": self.unit_of_measurement,
            "unique_id": self.unique_id,
            "value_template": self._value_template,
        }

        if self._icon:
            payload["icon"] = self.icon

        device = {
            "topic": self._config_topic,
            "payload": json.dumps(payload),
        }

        return device
