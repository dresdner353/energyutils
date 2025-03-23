#!/bin/bash
set -e

WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

if test -f "${WIFI_CONFIG_FILE}"; then
    echo "$WIFI_CONFIG_FILE found"
    DIR=`dirname ${WIFI_CONFIG_FILE}`

    # check if already processed
    DONE_FILE="${DIR}/PROCESSED.txt"
    if test -f "${DONE_FILE}"; then
        echo "${WIFI_CONFIG_FILE} already processed"
        exit
    fi

    . "$WIFI_CONFIG_FILE"
    rm -f /etc/NetworkManager/system-connections/*
    cat /home/pi/energyutils/solar_monitor/rpi.nmconnection.tmpl | \
        sed -e "s/__SSID__/${SSID}/g" -e "s/__PASSWORD__/${PASSWORD}/g" > \
        /etc/NetworkManager/system-connections/solarmon.nmconnection
    chmod go-rw /etc/NetworkManager/system-connections/solarmon.nmconnection
    systemctl restart NetworkManager
    echo "Configured WiFi for ${SSID}"

    # mark as processed
    touch ${DONE_FILE}
fi


