#!/bin/bash

# determine path of this script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

SHELLY_MON_WEB_SVR="shelly_monitor.py"
SHELLY_MON_WEB_SVR_PATH="${SCRIPTPATH}/${SHELLY_MON_WEB_SVR}"

LOG_FILE=/dev/null
#LOG_FILE=/home/pi/shelly_monitor.log

# Check if running
pgrep -f "${SHELLY_MON_WEB_SVR}" >/dev/null
if [ $? -ne 0 ]
then
    nohup python3 ${SHELLY_MON_WEB_SVR_PATH} > ${LOG_FILE} 2>&1 &
fi

exit 0
