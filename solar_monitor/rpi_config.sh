#!/bin/bash

CONFIG_FILE=`find /media -name config.json | tail -1`
SOLARMON_CONFIG_FILE='/home/pi/energyutils/solar_monitor/config.json'

NM_CONN_DIR="/etc/NetworkManager/system-connections"
NM_CONN_FILE="${NM_CONN_DIR}/solarmon.nmconnection"
NM_CONN_TMPFILE="/tmp/solarmon.nmconnection"
WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

OFFLINE_FILE="/tmp/OFFLINE"
OFFLINE_RESTART_DELAY=1200  # seconds

REBOOT=0

# Online test
# used to restart kiosk when going back online
ping -q -c 1 -w 1 www.google.com >/dev/null 2>&1
ONLINE=$?
if [ $ONLINE -ne 0 ]
then
    # offline
    # only touch file if it doesn't exist
    if [ ! -f "${OFFLINE_FILE}" ]
    then
        touch ${OFFLINE_FILE}
    fi
else
    # online
    # if known to be offline
    # restart kiosk and delete file
    if [ -f "${OFFLINE_FILE}" ]
    then
        systemctl restart solarmon_kiosk
        rm -f ${OFFLINE_FILE}
    fi
fi

# offline delayed 20 minutes 
# restart network and services
if [ -f "${OFFLINE_FILE}" ]
then
    NOW_TS=`date +%s`
    OFFLINE_TS=`stat -c %Y ${OFFLINE_FILE}`
    OFFLINE_DELTA=`expr ${NOW_TS} - ${OFFLINE_TS}`

    if [ "$OFFLINE_DELTA" -ge "${OFFLINE_RESTART_DELAY}" ] 
    then
        echo "Network offline over ${OFFLINE_RESTART_DELAY} seconds"
        echo "Restarting NetworkManager and services"
        # remove offline file and restart network/services
        rm -f ${OFFLINE_FILE}
        systemctl restart NetworkManager
        sleep 10
        systemctl restart solarmon
        systemctl restart solarmon_kiosk
    fi
fi

# JSON config file
if [ -f "${CONFIG_FILE}" ]
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
if [ -f "${WIFI_CONFIG_FILE}" ]
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

