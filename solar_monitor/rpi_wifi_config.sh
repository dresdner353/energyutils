#!/bin/bash
set -e

NM_CONN_DIR="/etc/NetworkManager/system-connections"
NM_CONN_FILE="${NM_CONN_DIR}/solarmon.nmconnection"
NM_CONN_TMPFILE="/tmp/solarmon.nmconnection"

WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

if test -f "${WIFI_CONFIG_FILE}"
then
    echo "$WIFI_CONFIG_FILE found"
    cat "$WIFI_CONFIG_FILE"
    # source variables
    . "$WIFI_CONFIG_FILE"

    # create NetworkManager connection file from template
    cat /home/pi/energyutils/solar_monitor/rpi.nmconnection.tmpl | \
        sed -e "s/__SSID__/${SSID}/g" -e "s/__PASSWORD__/${PASSWORD}/g" > ${NM_CONN_TMPFILE}

    if cmp -s "${NM_CONN_TMPFILE}" "${NM_CONN_FILE}"
    then
        echo "No changes to NetworkManager configuration"
    else
        echo "Updating NetworkManager configuration"
        # move to NetworkManager directory
        # and restart NetworkManager
        rm -f ${NM_CONN_DIR}/*
        mv ${NM_CONN_TMPFILE} ${NM_CONN_FILE}
        chmod go-rw ${NM_CONN_FILE}
        systemctl restart NetworkManager
        echo "Configured WiFi for ${SSID}"

        # reboot
        # not needed but helps clear down anu UI
        # disk insertion noise that may be on screen 
        /usr/sbin/reboot
    fi
fi


