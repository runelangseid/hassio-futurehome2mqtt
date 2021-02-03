#!/usr/bin/env bashio
set +u

CONFIG_PATH=/data/options.json
export FIMPSERVER=$(jq --raw-output ".fimpserver" $CONFIG_PATH)
export FIMPUSERNAME=$(jq --raw-output ".fimpusername" $CONFIG_PATH)
export FIMPPASSWORD=$(jq --raw-output ".fimppassword" $CONFIG_PATH)
export FIMPPORT=$(jq --raw-output ".fimpport" $CONFIG_PATH)
export CLIENT_ID=$(jq --raw-output ".client_id" $CONFIG_PATH)
export DEBUG=$(jq --raw-output ".debug" $CONFIG_PATH)
export SELECTED_DEVICES=$(jq --raw-output ".selected_devices" $CONFIG_PATH)
export PYTHONUNBUFFERED=1

echo Starting Futurehome FIMP to MQTT
python3 run.py serve
