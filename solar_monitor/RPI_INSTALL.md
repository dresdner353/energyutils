# SolarMon Raspberry Pi Setup

## Install steps for a Raspberry pi kiosk
If you have a raspberry pi that has a recent image installed, then these steps will download an install script and install everything automatically. 

Login as pi to the rpi and open a terminal, running the following command:
```
 curl -s https://raw.githubusercontent.com/dresdner353/energyutils/master/solar_monitor/rpi_install.sh | sudo bash
```

This step will do the following:
* Install python3 modules "requests", "dateutil" and "cherrypy" 
* download the code to the home directory of user "pi"
* Set up a systemctl service called solar_monitor to auto start the service on boot
* Copy a kiosk shell script into ~/.config/autostart which starts chromium bowser on login and points to the http://localhost:8090 page

The idea here is to use the rpi as a kiosk. You would also need to configure the pi to auto-login as user pi everytime it boots and the end result should be a functioning kiosk that shows the dashboard
 
