# Home Assistant add-on: Futurehome FIMP to MQTT

## About

This [Futurehome FIMP](https://github.com/futurehomeno/fimp-api) to MQTT add-on allows you to integrate the Futurehome
Smarthub with Home Assistant by using the local MQTT broker inside the hub.

While it is possible to configure Home Assistant the FIMP protocol
directly is a lot of work, and auto discovery is not possible.

This addon configure devices and their capabilities from Future Home in Home Assistant using [MQTT Discovery](https://www.home-assistant.io/integrations/mqtt/).

Read more about the [FIMP protocol](https://github.com/futurehomeno/fimp-api).

## Supported Futurehome devices

- Appliances (switches in HA)
  - Wall plugs like Fibaro Wall plug is supported
- Boiler
  - Connected with a relay device (e.g Futurehome Puck Relay)
- Lights (lights in HA)
  - Dimmers - On/Off and brightness. Tested with Fibaro dimmer 2
  - Switches - On/Off. Tested with Fibaro wall plug
- Locks
  - Basic unlock/lock for doorlocks. Tested with IDLock 150 (Unlock commands are currently not supported on Zigbee)
- Thermostats
  - Set mode
  - Set target temp
  - Read current measured temperature (Note that the temperature sensor that have the "Set as main temp sensor" checkbox checked in the Futurehome app will be used)
  - Change fan speed if device supports it (e.g Sensibo)
- Sensors
  - Battery
  - Illuminance
  - Presence
  - Temperature
  - Humidity
  - Contact
  - Meter_elec sensors (varies from device to device if they are supported)
    - Accumulated energy usage (kWh)
    - Power (W)
    - Voltage (V)
    - Current (A)
    - p_import (W)
    - e_import (kWh)
    - p_import_react (var)
    - p_export_react (var)
- Modus (home, away, sleep and vacation)
  - Set in entity `select.fh_mode`
- Shortcuts

## Known issues / limitations

- Chargepoint (FH Charge, Easee, Zaptec etc.) is not currently supported
- Scene control (Fibaro button, Heatit Z-Push 4 etc.) is not currently supported
- Blinds are not currently supported
- Sirens are not currently supported
- Leak detectors are not currently supported
- Garage doors are not currently supported
- Music players (Sonos etc.) is not currently supported - use Sonos integration in Home Assistant
- Some devices might still use sensor_power (deprecated) and sensor_voltage (deprecated) instead of `meter_elec`. This needs to be fixed by Futurehome.
- Shortcuts triggered externally (e.g from Futurehome app) is not logged in logbook

# Configuration and installation

> [!IMPORTANT]
>
> You need to enable local API access over MQTT from the Futurehome app.
>
> `Settings -> household -> hub settings -> local API setup`

### 1. Home Assistant configuration

Home Assistant must use the MQTT broker provided by the Futurehome Smarthub.
It's recommended to configure MQTT via GUI, and not via `.yaml`

Settings -> Device & services -> add integration -> search for `MQTT` -> select `MQTT` -> fill in hub IP and credentials. (NOTE that port should be 1884):

```
  broker: *hub ip*
  username: *username*
  password: *password*
  port: 1884
  discovery: true
  discovery_prefix: homeassistant
```

### 2. Install add-on

1. Add this repo as an add-on repository
   - Settings -> Add-ons -> Add-on store -> 3 dots in top right -> repositories -> paste link to this repository -> add
2. Install the addon 'Futurehome FIMP to MQTT'
   - Select `Futurehome FIMP integration` in the Add-on store -> install
3. Configure the addon with the same parameters as before
   - If you want to include or exclude certain devices, please specify with radio buttons, and then the devices in `selected_devices` with this format: \<adapter>\_\<address>. If you want to include all supported devices, leave radio button on `default`. Devices without a room will be ignored.
      - `adapter` is `zw` for Z-Wave devices
      - `adapter` is `zb` for Zigbee devices
      - For other adapters the name of the adapter is used - e.g `sensibo`
      - Examples:
        - zw_22
        - zb_47
        - sensibo_abCDEFgE
   - Toggle the switches to your desired likings for mode and shortcuts.
4. Start it. Supported devices should appear in the Home Assistant UI

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
   ```bash
   cp env-dist .env
   ```
2. Edit `.env` and fill in hostnames and credentials

3. Run `python run.py`

# Alternative FIMP integrations

Look at [here](yaml_manual_examples.md) for examples on how to add Wall plugs and sensors manually in `configuration.yaml`, using MQTT without the use of this addon.
