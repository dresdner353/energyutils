#!/bin/bash
set -e

CONFIG_FILE=`find /media -name config.json | tail -1`
SOLARMON_CONFIG_FILE='/home/pi/energyutils/solar_monitor/config.json'

NM_CONN_DIR="/etc/NetworkManager/system-connections"
NM_CONN_FILE="${NM_CONN_DIR}/solarmon.nmconnection"
NM_CONN_TMPFILE="/tmp/solarmon.nmconnection"
WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

OFFLINE_FILE="/tmp/OFFLINE"

REBOOT=0

# Online test
# used to restart kiosk when going back online
ping -q -c 1 -w 1 www.google.com >/dev/null 2>&1
ONLINE=$?
if [ $ONLINE -ne 0 ]
then
    # offline
    touch ${OFFLINE_FILE}
else
    # online
    if test -f "${OFFLINE_FILE}"
    then
        # restart kiosk
        systemctl restart solarmon_kiosk
        rm -f ${OFFLINE_FILE}
    fi
fi

# JSON config file
if test -f "${CONFIG_FILE}"
then
    echo "${CONFIG_FILE} found"
    if cmp -s "${CONFIG_FILE}" "${SOLARMON_CONFIG_FILE}"
    then
        echo "No changes to SolarMon configuration"
    else
        echo "Updating SolarMon configuration"
        cp ${CONFIG_FILE} ${SOLARMON_CONFIG_FILE}
        chown pi:pi ${SOLARMON_CONFIG_FILE}
        chmod go-rw ${SOLARMON_CONFIG_FILE}
        chmod u+rw ${SOLARMON_CONFIG_FILE}
        REBOOT=1
    fi
fi

# WiFi config file
if test -f "${WIFI_CONFIG_FILE}"
then
    echo "$WIFI_CONFIG_FILE found"
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
        REBOOT=1
    fi
fi

if [[ "${REBOOT}" -eq 1 ]]
then
    /usr/sbin/reboot
fi

