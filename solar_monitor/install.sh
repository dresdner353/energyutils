#!/bin/bash

# Exit on errors
set -x

# install
function install_solar_monitor {
    cd # go to home
    echo "Installing energyutils user:${USER} pwd:${HOME}"

    # GIT repo
    echo "Downloading energyutils..."
    rm -rf energyutils
    git clone https://github.com/dresdner353/energyutils.git
}

# export function for su call
export -f install_solar_monitor 

# main()
if [[ "`whoami`" != "root" ]]
then
    echo "This script must be run as root (or with sudo)"
    exit 1
fi

# Create account for solarmon
USER=solarmon
PASSWORD='123456789'
HOME_DIR=/home/${USER}

adduser --disabled-password --comment '' ${USER} --home ${HOME_DIR}
printf "${PASSWORD}""\n""${PASSWORD}""\n" | passwd ${USER}

# install packages
apt-get update
apt install python3-dateutil python3-cherrypy3

# download code
su ${HOME_USER} -c "bash -c install_solar_monitor"

# install and start service
cp ${HOME_DIR}/energyutils/solar_monitor/solarmon.service /etc/systemd/system
systemctl daemon-reload
systemctl enable solarmon
systemctl restart solarmon
