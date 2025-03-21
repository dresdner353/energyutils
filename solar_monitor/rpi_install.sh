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

    # browser kiosk
    AUTOSTART_DIR=.config/autostart
    mkdir -p ${AUTOSTART_DIR}
    cp energyutils/solar_monitor/chromium_kiosk.desktop ${AUTOSTART_DIR}
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
apt install git unclutter python3-requests python3-dateutil python3-cherrypy3

# download code as tareget user
su ${USER} -c "bash -c install_solar_monitor"

# install and start service
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon.service /etc/systemd/system
systemctl daemon-reload
systemctl enable solarmon
systemctl restart solarmon
