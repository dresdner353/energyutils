#!/bin/bash

# loop until monitor is detected running
while true
do
    echo "Checking for running solar monitor.."
    MON_CHECK=`netstat -nl | grep :8090 | wc -l`

    if [ ${MON_CHECK} -eq 1 ]
    then
        echo "solar monitor is up"
        break
    fi

    sleep 5
done

# give more time for the monitor to be available
sleep 20

# chromium kiosk
echo "Starting Chromium in kiosk mode"
killall -9 chromium-browser 
export DISPLAY=:0

# disable screen blanking and move mouse to 0,0
xset s 0
xset -dpms
xdotool mousemove --sync 0 0

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

# launch chrome against the Solarmon dashboard 
# with layout forced to large and margin of 3 for handling of overscan
chromium-browser "${flags[@]}" --app='http://localhost:8090?layout=large&margin=3' 
