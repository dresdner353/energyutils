#!/bin/bash

# loop until monitor is detected running
while true
do
    echo "Checking for running Shelly monitor.."
    MON_CHECK=`netstat -nl | grep :8090 | wc -l`

    if [ ${MON_CHECK} -eq 1 ]
    then
        echo "Shelly monitor is up"
        break
    fi

    sleep 5
done

sleep 5

# firefox kiosk
echo "Starting Firefox in kiosk mode"
killall -9 firefox
firefox -kiosk http://localhost:8090
