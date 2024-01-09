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

# chromium kiosk
echo "Starting Chromium in kiosk mode"
killall -9 chromium-browser
chromium-browser \
    --disable-translate \
    --disable-infobars \
    --disable-suggestions-service \
    --disable-save-password-bubble \
    --noerrdialogs \
    --disable-component-update \
    --kiosk http://localhost:8090
