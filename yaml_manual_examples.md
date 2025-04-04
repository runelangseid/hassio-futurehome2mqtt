# Alternative FIMP integrations

Here are examples on how to add Wall plugs and sensors manually in `configuration.yaml`, using MQTT without the use of this addon.

## Wall plug (Fibaro)

Replace '34' with the address for the device in Futurehome.

```
mqtt:
  #
  # Kontor
  #
  # Wall plug
  switch:
    - name: "Wall plug (kontor)"
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
mqtt:
  # Fibaro Eye
  sensor:
    - name: "Batteri Kontor"
      state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:battery/ad:37_0"
      unit_of_measurement: '%'
      value_template: "{{ value_json.val }}"

    - name: "Bevegelse Kontor"
      state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_presence/ad:37_0"
      value_template: "{{ value_json.val }}"

    - name: "Temperatur Kontor"
      state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_temp/ad:37_0"
      unit_of_measurement: '°C'
      value_template: "{{ value_json.val }}"

    - name: "Lysstyrke Kontor"
      state_topic: "pt:j1/mt:evt/rt:dev/rn:zw/ad:1/sv:sensor_lumin/ad:37_0"
      unit_of_measurement: 'Lux'
      value_template: "{{ value_json.val }}"
```
