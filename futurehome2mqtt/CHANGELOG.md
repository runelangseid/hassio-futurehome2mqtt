## 0.2

* Huge code rewrite. Code base has been reduced
* Most things from 0.1 should work
  * Dimmers for lightning
  * Binary switches for appliances (not lightning)
  * Sensors: battery, illuminance, temperature, electric meters
* Modus switch is not re-implemented yet
* Internal bridge for Dimmer lights have been removed, reducing complexity in addon
* Entities are now generated based on device id Futurehome and not the name using `object_id`
* Simplified configuration. No need for long-lived token and uptime sensor as HA announces restarts via MQTT
* Rewritten MQTT discovery
* Added Energy sensor for all devices which supports this (´meter_elec`)
