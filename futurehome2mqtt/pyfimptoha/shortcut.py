import json

def new_button(mqtt, shortcut, debug):
    """
    Creates buttons in Home Assistant for each shortcut created in Futurehome
    """

    shortcut_id = str(shortcut["id"])
    shortcut_name = shortcut["client"]["name"]
    identifier = f"fh_shortcut_{shortcut_id}"
    command_topic = "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
    component = {
        "icon": "mdi:arrow-right-bold-hexagon-outline",
        "name": f"{shortcut_name}",
        "object_id": identifier,
        "unique_id": identifier,
        "device": {
            "identifiers": "futurehome_smarthub",
            "name": "Futurehome Smarthub",
            "suggested_area": "Futurehome Smarthub",
            "manufacturer": "Futurehome"
        },
        "command_topic": command_topic,
        "command_template": f"""{{
            "serv": "vinculum",
            "type": "cmd.pd7.request",
            "val_t": "object",
            "val": {{
                "cmd": "set",
                "component": "shortcut",
                "id": {int(shortcut_id)}
            }},
            "resp_to": "pt:j1/mt:rsp/rt:app/rn:homeassistant-client/ad:1",
            "src": "homeassistant",
            "ver": "1",
            "uid": "e523c0a7-40d7-48fc-ab55-2a58f8feb1f1",
            "topic": "pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1"
            }}
        """
        # Why double braces are used;
        # https://stackoverflow.com/questions/5466451/how-do-i-escape-curly-brace-characters-in-a-string-while-using-format-or/5466478#5466478
    }

    payload = json.dumps(component)
    mqtt.publish(f"homeassistant/button/{identifier}/config", payload)
    if debug:
        print(f"Creating button device for shortcut id: {shortcut_id}")


    # Device trigger - logs triggered shortcuts from e.g Futurehome app
    # TODO ? implement a way to register shortcuts triggered externally (e.g from Futurehome app) via automations.

    # alias: Log external triggers of shortcuts
    # description: ""
    # trigger:
    #   - platform: mqtt
    #     topic: pt:j1/mt:cmd/rt:app/rn:vinculum/ad:1
    # condition:
    #   - condition: template
    #     value_template: >
    #       {{ trigger.payload_json.val.cmd == 'set' and
    #       trigger.payload_json.val.component == 'shortcut' }}
    # action:
    #   - service: logbook.log
    #     metadata: {}
    #     data:
    #       name: External service (e.g Futurehome app)
    #       message: triggered a shortcut
    #       entity_id: button.fh_shortcut_{{ trigger.payload_json.val.id }}
    # mode: single
