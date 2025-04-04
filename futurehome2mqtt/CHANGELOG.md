## 0.3.8

- Added option to select if you want to include or exclude mode & shortcuts
- Updated README
  - Expample for `selected_devices_mode`
- Updated repository.json & config.json to current maintainer

## 0.3.7

- Updated README
- Changed `selected_devices_mode` default option from 'ignored' to 'default' to include all supported devices.

## 0.3.6

- Added more sensors in meter_elec
  - p_import
  - e_import
  - p_import_react
  - p_export_react
- Added 'boiler' type as switch
- (dev) Some cleanup in meter_elec.py

## 0.3.5

- Added support for contact sensors
  - Subtypes `door`, `window`, `garage` supported
- Added more checks on reports from sensors
- Added support to select if you want to include or excluding certain devices from being synced
- Move mode and shortcut to one device "Futurehome Smarthub"
- Updated README
  - Support for contact sensor
  - Describing the selected_devices in configuration
- (dev) Added symbolic link for README.md into `futurehome2mqtt` directory.
  This allows the add-on store to show the content of README.md instead of nothing.
- (dev) Refactored client.py, and removed fimp.py
- (dev) Changed env variables to snake_case for readability
- (dev) Changed from `str` to `password` for fimp_password on configuration screen
- (dev) Added breaking_versions to config file
- (dev) Temporarily fixed debug option - verbose logging enabled if option is set to true.
  Plan to use better logger with loglevels.
- (dev) Removed name from device object for sensor_temp.
  This will prevent device name for Heatit z-trm3 to be overwritten with the sensor name

## 0.3.4

- Removed unused dependency 'requests'

## 0.3.3

- Added logo and icon
- Fixes: On some thermostats (e.g Heatit) you are currently not able to readout current
  measured temperature (room temp sensor or floor temp sensor) directly on the thermostat card as it is on a different device.

Note that the temperature sensor that have the "Set as main temp sensor" checkbox checked in the Futurehome app will be used.

## 0.3.2

- Added basic HAN sensor support
- Updated README
  - Clearer installation instructions
  - Added 'Known issues' section

## 0.3.1

- Fixes: Fails to install on Home Assistant. Error: `The command '/bin/ash -o pipefail -c apk add --no-cache python3 py-pip && pip3 install --upgrade pip' returned a non-zero code: 1`
- (dev) moved devcontainer.json file to the recommended folder. Ref [docs](https://developers.home-assistant.io/docs/add-ons/testing/)

## 0.3.0

### Breaking changes

Note that version 0.3.x includes breaking changes from 0.2.x.
This is mainly due to the refactor to include adapter name in the identifiers, and how entities are grouped to one device.
You may have to update all entities in dashboards and automations etc.

### New, fixed, and improved:

- Huge code rewrite to be more adaptive
- Added basic lock/unlock for doorlocks. Tested with IDLock 150 (Unlock commands are currently not supported on Zigbee)
- Added thermostat support
  - Set mode
  - Set target temp
  - Change fan speed if device supports it (e.g Sensibo)
- Added humidity sensor
- Fixed `meter_elec` service for accumulated energy usage (kWh)
- Expanded `meter_elec` service for devices that supports this:
  - Power (W)
  - Voltage (V)
  - Current (A)
- Changed mode sensor to be a (dropdown) select, so you are able to switch mode
- Added shortcuts support
- Added room support
  - Devices will be placed in rooms with the same names as Futurehome. If the room does not exist it will be created
- All devices now generate MQTT devices and group all common sensors and controls
- (dev) added .env file to be sourced with `python-dotenv`

### Planned and work in progress:

- HAN sensor support
- On some thermostats (e.g Heatit) you are currently not able to readout current
  measured temperature (room temp sensor or floor temp sensor) directly on the thermostat card as it is on a different device
- Fails to install on Home Assistant. Error: `The command '/bin/ash -o pipefail -c apk add --no-cache python3 py-pip && pip3 install --upgrade pip' returned a non-zero code: 1`

### Known issues:

- Some devices might still use sensor_power (deprecated) and sensor_voltage (deprecated) instead of `meter_elec`

## 0.2.2

- Added mode sensor as `sensor.fh_mode` (home, away, sleep, vacation). Read only

## 0.2.1

- Added presence sensors

## 0.2

- Huge code rewrite. Code base has been reduced
- Most things from 0.1 should work
  - Dimmers for lightning
  - Binary switches for appliances and lightning
  - Sensors: battery, illuminance, temperature, electric meters
- Modus switch is not re-implemented yet
- Internal bridge for Dimmer lights have been removed, reducing complexity in addon
- Entities are now generated based on device id Futurehome and not the name using `object_id`
- Simplified configuration. No need for long-lived token and uptime sensor as HA announces restarts via MQTT
- Rewritten MQTT discovery
- Added Energy sensor for all devices which supports this (´meter_elec`)
