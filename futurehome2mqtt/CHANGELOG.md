## 0.2

* Only lights with dimming is currently supported (probably). Do NOT upgrade if 0.1.x works for you
* Huge code rewrite. Code base has been reduced
* Internal bridge for Dimmer lights have been removed, reducing complexity in addon
* Simplified configuration. No need for long-lived token and uptime sensor. HA restarts are announced via MQTT
* Rewritten MQTT discovery
* Added Energy sensor for all devices which supports this (´meter_elec`)
