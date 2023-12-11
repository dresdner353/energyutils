# Solar Monitor

Initial stab at a monitor web server designed to query live data from a Shelly EM and historic data from the cloud API and present it on a reactive web page that could be displayed on a monitor, or tablet screen. This will likely evolve to read data from solar inverters also via their respective cloud APIs. 


## Install steps for a Raspberry pi

* git clone https://github.com/dresdner353/energyutils.git  
Assuming this is done in the home directory of user pi (/home/pi)
* sudo apt install python3-dateutil python3-cherrypy  
Installs the required dateutil and cherrypy modules
* Add "* * * * * /home/pi/energyutils/solar_monitor/solar_monitor.sh" to crontab  
This is done with crontab -e and then paste in the above line. 
* Run that script manually or wait until cron starts it  
Check with ps -ef | grep python3 that you can see the solar_monitor running
* Browse to http://<rpi ip>:8090 to view the dashboard  
Bare bones data will be shown at first as it needs to be configured
* Browse to http://<rpi ip>:8090/admin to view the admin settings  
When prompted, login with username "admin" and pasword "123456789"
* Fill in details for the Shelly Cloud hostname, auth key, device ID, device LAN IP/mDNS hostname  
* You can also set username and password for the Shelly EM if you have enabled local LAN authentication
* Click the apply button and hopefully it should come to life
