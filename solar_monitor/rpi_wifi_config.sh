#!/bin/bash
set -e
cd /tmp

WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

if test -f "${WIFI_CONFIG_FILE}"; then
    echo "$WIFI_CONFIG_FILE found"
    DIR=`dirname ${WIFI_CONFIG_FILE}`
    . "$WIFI_CONFIG_FILE"
    cat /home/pi/energyutils/solar_monitor/rpi.nmconnection.tmpl | sed -e "s/__SSID__/${SSID}/g" -e "s/__PASSWORD__/${PASSWORD}/g" >solarmon.nmconnection
    rm -f /etc/NetworkManager/system-connections/*
    cp -f solarmon.nmconnection /etc/NetworkManager/system-connections
    systemctl restart NetworkManager
    echo "Configured WiFi for ${SSID}"
fi
