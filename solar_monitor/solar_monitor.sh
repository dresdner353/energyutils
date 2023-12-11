#!/bin/bash

# determine path of this script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

SOLAR_MON_WEB_SVR="solar_monitor.py"
SOLAR_MON_WEB_SVR_PATH="${SCRIPTPATH}/${SOLAR_MON_WEB_SVR}"

LOG_FILE=/dev/null
#LOG_FILE=/home/pi/solar_monitor.log

# Check if running
pgrep -f "${SOLAR_MON_WEB_SVR}" >/dev/null
if [ $? -ne 0 ]
then
    nohup python3 ${SOLAR_MON_WEB_SVR_PATH} > ${LOG_FILE} 2>&1 &
fi

exit 0
