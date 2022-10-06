import json

import paho.mqtt.client as mqtt

def send_discovery_request(client: mqtt):
    """Load FIMP devices from MQTT broker"""

    path = "pyfimptoha/data/fimp_discover.json"
    topic = "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
    with open(path) as json_file:
        data = json.load(json_file)

        payload = json.dumps(data)
        print('Asking FIMP to expose all devices...')
        client.publish(topic, payload)


# todo refactor. Used for tests
def load_json_device(self, filename):
    data = "{}"

    path = "data/%s" % filename
    with open(path) as json_file:
        data = json.load(json_file)

    # self._devices.append(data)
    return data
