# Solar Monitor

This is a small web server designed to query live data from the likes of a Shelly EM or inverter cloud API and present it on a reactive web page that could be displayed on a monitor, TV or tablet screen. 

## Basic steps to test
* git clone https://github.com/dresdner353/energyutils.git (or download the Zip file)
* For typical Windows/Mac/Linux: pip3 install python-dateutil cherrypy
* For Raspberry Pi: sudo apt install python3-dateutil python3-cherrypy3

To run:
* python3 energyutils/solar_monitor/solar_monitor.py 

Notes:
* The script will startup and create a default config.json file in energyutils/solar_monitor
* point your browser at http://localhost:8090 and you should see a blank black page displayed
* Browse to http://localhost:8090/admin to bring up the admin page (login as user "admin" and password "123456789")
* Select the inverter/data source type and go from there. 
* When ready to save, click the apply button
* If the Shelly or inverter credentials are correct, then actual usage data should soon appear on the main dashboard.
* For now, only Shelly EM and Solis inverters are supported. Others such as Sofar, Huawei and others will be added over time


## Install steps for a Raspberry pi kiosk
If you have a raspberry pi that has a recent image installed, then these steps will download an install script and install everything automatically. 

Login as pi to the rpi and open a terminal, running the following command:
* curl -s https://raw.githubusercontent.com/dresdner353/energyutils/master/solar_monintor/rpi_install.sh | sudo bash

This step will do the following:
* Install python3 dateutil and cherrypy (web server) modules
* download the code to the home directory of user "pi"
* Set up a systemctl service called solar_monitor to auto start the service on boot
* Copy a kiosk shell script into ~/.config/autostart which starts chromium bowser on login and points to the http://localhost:8090 page

The idea here is to use the rpi as a kiosk. You would also need to configure the pi to auto-login as user pi everytime it boots and the end result should be a functioning kiosk that shows the dashboard
 
