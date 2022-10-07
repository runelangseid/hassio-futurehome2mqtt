# Home Assistant add-on: Futurehome FIMP to MQTT

## About

This [Futurehome FIMP](https://github.com/futurehomeno/fimp-api) to MQTT add-on allows you to integrate the Futurehome
Smarthub with Home Assistant by using the local MQTT broker inside the hub.

While it is possible to configure Home Assistant the FIMP protocol
directly is a lot of work, and auto discovery is not possible.

This addon configure devices and their capabilities from Future Home in Home Assistant using MQTT Discovery.

Read more about the [FIMP protocol](https://github.com/futurehomeno/fimp-api).


## Supported Futurehome devices

* Appliances (switches in HA)
  * Wall plugs like Fibaro Wall plug is supported
* Lights (lights in HA)
  * Dimmers - On/Off and brightness. Tested with Fibaro dimmer 2
  * Switches - On/Off. Tested with Fibaro wall plug
* Energy
  * Accumulated energy usage (`meter_elec´) for devices supporting this


### Untested in new version

These things are probably no longer implemented

* Sensors (sensors in HA)
  * Battery
  * Illuminance
  * Power usage
  * Temperature
* Scene control. Exposed as sensor. Tested with Fibaro button, and Namron 4 channel (K8)
* Modus: home, away, sleep and vacation (`sensor.modus`, read only)

# Configuration and installation

### 1. Home Assistant configuration

Home Assistant must use the MQTT broker provided by the Futurehome Smart hub.

configuration.yaml
```
# MQTT
mqtt:
  # Futurehome smart hub
  broker: *hub ip*
  username: *username*
  password: *password*
  port: 1884
  discovery: true
  discovery_prefix: homeassistant
```

### 2. Install add-on

1) Add this repo as a add-on repository
2) Install the addon 'Futurehome FIMP to MQTT'
3) Configure the addon with the same parameters as before
4) Start it. Supported devices should appear in the Home Assistant UI


# Development

As this addon is not dependent on Home Assistant it's easiest to develop
new features locally, or by using the Dev Container capabilities in VS Code
which provides a full Home Assistant setup.

## Using virtual env

### Git clone and installation
```
git clone https://github.com/runelangseid/hassio-futurehome2mqtt
cd hassio-futurehome2mqtt/futurehome2mqtt
virtualenv venv  # You might need to specify python 3 somehow: virtualenv -p python3.7 venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration

1. Setup configuration
    ```
    cp env-dist .env
    ```
2. Edit `.env` and fill in hostnames and credentials

3. Run `source .env && python run.py serve`


# Alternative FIMP integrations

Below are examples on how to add Wall plugs and sensors manually to Home Assistant
using MQTT without the use of this addon.

## Wall plug (Fibaro)

Replace '34' with the address for the device in Futurehome.

```
switch:
  #
  # Kontor
  #
  # Wall plug
  - platform: mqtt
    name: "Wall plug (kontor)"
    state_topic:   "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:out_bin_switch/ad:34_0"
    command_topic: "pt:j1/mt:cmd/rt:dev/rn:zw/ad:1/sv:out_bin_switch/ad:34_0"
    value_template: '{{ value_json.val }}'
    payload_on:  '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":true,"val_t":"bool"}'
    payload_off: '{"props":{},"serv":"out_bin_switch","tags":[],"type":"cmd.binary.set","val":false,"val_t":"bool"}'
    state_on: true
    state_off: false
```

## Multi Sensor (Fibaro)

Replace '37' with the address for the device in Futurehome.

```
  # Øye (kontor)
  - platform: mqtt
    name: "Batteri Kontor"
    state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:battery/ad:37_0"
    unit_of_measurement: '%'
    value_template: "{{ value_json.val }}"
  - platform: mqtt
    name: "Bevegelse Kontor"
    state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_presence/ad:37_0"
    value_template: "{{ value_json.val }}"
  - platform: mqtt
    name: "Temperatur Kontor"
    state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_temp/ad:37_0"
    unit_of_measurement: '°C'
    value_template: "{{ value_json.val }}"
  - platform: mqtt
    name: "Lysstyrke Kontor"
    state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_lumin/ad:37_0"
    unit_of_measurement: 'Lux'
    value_template: "{{ value_json.val }}"
```
