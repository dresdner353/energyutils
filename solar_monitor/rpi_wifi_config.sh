#!/bin/bash
set -e

NM_CONN_DIR="/etc/NetworkManager/system-connections"
NM_CONN_FILE="${NM_CONN_DIR}/solarmon.nmconnection"

WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

if test -f "${WIFI_CONFIG_FILE}"; then
    echo "$WIFI_CONFIG_FILE found"
    DIR=`dirname ${WIFI_CONFIG_FILE}`

    . "$WIFI_CONFIG_FILE"
    rm -f ${NM_CONN_DIR}/*
    cat /home/pi/energyutils/solar_monitor/rpi.nmconnection.tmpl | \
        sed -e "s/__SSID__/${SSID}/g" -e "s/__PASSWORD__/${PASSWORD}/g" > ${NM_CONN_FILE}
    chmod go-rw ${NM_CONN_FILE}
    systemctl restart NetworkManager
    echo "Configured WiFi for ${SSID}"

    # reboot
    /usr/sbin/reboot
fi


