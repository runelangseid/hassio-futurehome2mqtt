#!/usr/bin/with-contenv bashio
set -e

export FIMP_SERVER=$(bashio::config 'fimp_server')
export FIMP_USERNAME=$(bashio::config 'fimp_username')
export FIMP_PASSWORD=$(bashio::config 'fimp_password')
export FIMP_PORT=$(bashio::config 'fimp_port')
export CLIENT_ID=$(bashio::config 'client_id')
export DEBUG=$(bashio::config 'debug')
export SELECTED_DEVICES_MODE=$(bashio::config 'selected_devices_mode')
export SELECTED_DEVICES=$(bashio::config 'selected_devices')
export INCLUDE_MODE=$(bashio::config 'include_mode')
export INCLUDE_SHORTCUTS=$(bashio::config 'include_shortcuts')
export PYTHONUNBUFFERED=1

echo Starting Futurehome FIMP to Home Assistant
python3 run.py
