#!/bin/bash

# loop until monitor is detected running
while true
do
    echo "Checking for running solar monitor.."
    curl http://127.0.0.1:8090 > /dev/null 2>&1
    if [ ${?} -eq 0 ]
    then
        echo "solar monitor is up"
        break
    fi
    sleep 5
done

# give more time for the monitor to be available
sleep 30

# chromium kiosk
echo "Starting Chromium in kiosk mode"
killall -9 chromium-browser 
export DISPLAY=:0

# wipe any local chromium config
cd
rm -rf .config/chromium
rm -rf .cache/chromium

# disable screen blanking and move mouse to 0,0
xset s off
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
# with forced margin of 3 for handling of overscan
chromium-browser "${flags[@]}" --app='http://localhost:8090?margin=3' 
