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

flags=(
   --kiosk
   --touch-events=enabled
   --disable-pinch
   --noerrdialogs
   --enable-features=OverlayScrollbar
   --disable-session-crashed-bubble
   --simulate-outdated-no-au='Tue, 31 Dec 2099 23:59:59 GMT'
   --disable-component-update
   --disable-features=TranslateUI
   --autoplay-policy=no-user-gesture-required
)

chromium-browser "${flags[@]}" --app=http://localhost:8090 &

# get the mouse out of the way
sleep 10
echo "moving mouse out of the way"
xdotool mousemove 0 9000

