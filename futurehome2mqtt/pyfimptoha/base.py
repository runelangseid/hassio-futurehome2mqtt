class Base:
    _name = ""
    _address = None
    _room = ""
    _service_name = None
    _unique_id = None

    _config_topic = None
    _command_topic = None

    def __init__(self, service_name, service, device):
        self._address = device["fimp"]["address"]
        self._device = device
        self._name = device["client"]["name"]
        self._room = device["room"]
        self._service = service
        self._service_name = service_name
        self._unique_id = self._address + "-" + service_name
        self._config_topic = "homeassistant/sensor/%s/config" % (self._unique_id)

    @property
    def unique_id(self):
        '''Return the unique id of the light.'''
        return self._unique_id
