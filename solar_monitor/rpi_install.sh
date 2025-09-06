#!/bin/bash

# Exit on errors
set -e

# install
function install_solar_monitor {
    set -e # exit on errors
    cd # go to home
    echo "Installing energyutils user:${USER} pwd:${HOME}"

    # backup any existing config installer logo
    echo "Backing up config..."
    if [ -f energyutils/solar_monitor/config.json ]; then
        mv energyutils/solar_monitor/config.json /tmp
    fi
    if [ -f energyutils/solar_monitor/www/images/installer.png ]; then
        mv energyutils/solar_monitor/www/images/installer.png /tmp
    fi

    # GIT repo wipe and install
    rm -rf energyutils
    echo "Downloading energyutils..."
    git clone https://github.com/dresdner353/energyutils.git

    # restore config and logo
    echo "Restoring config..."
    if [ -f /tmp/config.json ]; then
        mv /tmp/config.json energyutils/solar_monitor
    fi
    if [ -f /tmp/installer.png ]; then
        mv /tmp/installer.png energyutils/solar_monitor/www/images
    fi

    # wipe chromium config and cache
    rm -rf .config/chromium
    rm -rf .cache/chromium
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
echo "Installing required packages..."
apt-get update
apt install git unclutter xdotool zenity ttf-mscorefonts-installer python3-requests python3-dateutil python3-cherrypy3

# download code as target user
su ${USER} -c "bash -c install_solar_monitor"

# mdns hostname solarmon.local
echo "Setting hostname..."
echo 'solarmon' > /etc/hostname

# Wifi setup via USB stick
# root cron job every minute
echo "Configuring crontab..."
chmod +x /home/pi/energyutils/solar_monitor/rpi_config.sh
echo '# SolarMon cron tasks' > /tmp/crontab
echo ' ' >> /tmp/crontab
echo '# Config check via USB stick every minute ' >> /tmp/crontab
echo '* * * * * /home/pi/energyutils/solar_monitor/rpi_config.sh >>/dev/null 2>&1' >> /tmp/crontab
echo ' ' >> /tmp/crontab
echo '# Daily restart of services at 06:00, 18:00' >> /tmp/crontab
echo '0 6,18 * * * /usr/bin/systemctl restart solarmon' >> /tmp/crontab
echo '5 6,18 * * * /usr/bin/systemctl restart solarmon_kiosk' >> /tmp/crontab

# load the crontab
crontab /tmp/crontab

# install and start service
echo "Configuring systemd services..."
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon.service /etc/systemd/system
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon_kiosk.service /etc/systemd/system
systemctl daemon-reload
systemctl enable solarmon
systemctl enable solarmon_kiosk
systemctl restart solarmon
systemctl restart solarmon_kiosk
