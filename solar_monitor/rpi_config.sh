#!/bin/bash

CONFIG_FILE=`find /media -name config.json | tail -1`
SOLARMON_CONFIG_FILE='/home/pi/energyutils/solar_monitor/config.json'

NM_CONN_DIR="/etc/NetworkManager/system-connections"
NM_CONN_FILE="${NM_CONN_DIR}/solarmon.nmconnection"
NM_CONN_TMPFILE="/tmp/solarmon.nmconnection"
NM_CONN_TMPL="/home/pi/energyutils/solar_monitor/rpi.nmconnection.tmpl"
WIFI_CONFIG_FILE=`find /media -name wifi.txt | tail -1`

OFFLINE_FILE="/tmp/OFFLINE"
OFFLINE_RESTART_DELAY=1200  # seconds

function display_msg() {
    # display message using zenity
    # # run in background to avoid delays
    zenity \
        --timeout=5 \
        --info \
        --title "SolarMon" \
        --text "<span font=\"32\">${1}</span>" & 
}


# PATH and X11
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export DISPLAY=:0
xhost +

# Online test
wget -q --spider 'https://google.com' >/dev/null 2>&1
ONLINE=$?
if [ $ONLINE -ne 0 ]
then
    # offline
    display_msg "No Internet connection"
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
        display_msg "Internet connection restored"
        sudo systemctl restart solarmon_kiosk
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
        display_msg "Internet connection down for over 20 minutes"
        # remove offline file and restart network/services
        rm -f ${OFFLINE_FILE}
        sudo systemctl restart NetworkManager
        sudo systemctl restart solarmon
        sudo systemctl restart solarmon_kiosk
    fi
fi

# JSON config file
if [ -f "${CONFIG_FILE}" ]
then
    echo "${CONFIG_FILE} found"
    if cmp -s "${CONFIG_FILE}" "${SOLARMON_CONFIG_FILE}"
    then
        display_msg "SolarMon config file is already applied \n\n(remove USB drive)"
    else
        cp ${CONFIG_FILE} ${SOLARMON_CONFIG_FILE}
        chmod go-rw ${SOLARMON_CONFIG_FILE}
        chmod u+rw ${SOLARMON_CONFIG_FILE}
        display_msg "Applied new SolarMon config file \n\n(remove USB drive)"
        sudo systemctl restart solarmon
        sudo systemctl restart solarmon_kiosk
    fi
fi

# WiFi config file
if [ -f "${WIFI_CONFIG_FILE}" ]
then
    echo "$WIFI_CONFIG_FILE found"
    # source variables
    . "$WIFI_CONFIG_FILE"

    # create NetworkManager connection file from template
    cat ${NM_CONN_TMPL} | \
        sed -e "s/__SSID__/${SSID}/g" -e "s/__PASSWORD__/${PASSWORD}/g" > ${NM_CONN_TMPFILE}

    if sudo cmp -s "${NM_CONN_TMPFILE}" "${NM_CONN_FILE}"
    then
        display_msg "WiFi is already updated to ${SSID} \n\n(remove USB drive)"
    else
        # move to NetworkManager directory
        # and restart everything
        sudo rm -f ${NM_CONN_DIR}/*
        sudo mv ${NM_CONN_TMPFILE} ${NM_CONN_FILE}
        sudo chown root:root ${NM_CONN_FILE}
        sudo chmod go-rw ${NM_CONN_FILE}
        sudo systemctl restart NetworkManager
        sudo systemctl restart solarmon
        sudo systemctl restart solarmon_kiosk
        display_msg "Updated WiFi to ${SSID} \n\n(remove USB drive)"
    fi
fi
