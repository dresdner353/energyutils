#!/bin/bash

# Exit on errors
set -x

# install
function install_solar_monitor {
    cd # go to home
    echo "Installing energyutils user:${USER} pwd:${HOME}"

    # backup any existing config and wipe repo
    mv energyutils/solar_monitor/config.json /tmp
    rm -rf energyutils

    # GIT repo
    echo "Downloading energyutils..."
    git clone https://github.com/dresdner353/energyutils.git

    # restore config
    mv /tmp/config.json energyutils/solar_monitor
}

# export function for su call
export -f install_solar_monitor 

# main()
if [[ "`whoami`" != "root" ]]
then
    echo "This script must be run as root (or with sudo)"
    exit 1
fi

# target user is pi
# this is the only user that can be forced to auto-login
USER=pi
HOME_DIR=~pi

# install packages
apt-get update
apt install git unclutter xdotool ttf-mscorefonts-installer python3-requests python3-dateutil python3-cherrypy3

# download code as target user
su ${USER} -c "bash -c install_solar_monitor"

# mdns hostname solarmon.local
echo 'solarmon' > /etc/hostname

# Wifi setup via USB stick
# root cron job every minute
chmod +x /home/pi/energyutils/solar_monitor/rpi_config.sh
echo '* * * * * /home/pi/energyutils/solar_monitor/rpi_config.sh >>/dev/null 2>&1' > /tmp/crontab
crontab /tmp/crontab

# install and start service
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon.service /etc/systemd/system
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon_kiosk.service /etc/systemd/system
systemctl daemon-reload
systemctl enable solarmon
systemctl enable solarmon_kiosk
systemctl restart solarmon
systemctl restart solarmon_kiosk
