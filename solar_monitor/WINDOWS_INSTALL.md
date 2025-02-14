# SolarMon Windows Setup

## Download the energyutils codebase
* Browse to https://github.com/dresdner353/energyutils 
* From there, look for the green Code button, click it and select the download ZIP file 
* In Windows explorer, right-click and "extract all" files (as you might do with a zip file usually). 
  But do not double-click to open it as that will not work correctly. 


## Install Python3

* Launch the Microsoft Store and search for python3. 
* Install by clicking the "Get" button

Note: You need python 3.9 or later. At the time of writing, the version Microsoft had 
listed was 3.11


## Run initial setup script

* In the energy_utils/solar_monitor folder, double-click the batch script called "windows_setup".

Note:You may be warned about this as being an unknown program and feel free to 
virus scan etc. But depending on your virus scanner etc, you may have to 
Click on a "Run anyway" to kick it off. Windows Defender will popup a dialog with 
button "Don't run", but to run it, you click on the "More info" link and there is a 
"Run anyway" option to launch it.

This script only runs Python3 and installs required modules for 
the report scripts. 


## Run the Solar Monitor script

* In energyutils/solar_monitor folder, double-click on "windows_run".
* This will open a DOS window and start the script.
* You can access the dashboard by browsing to http://localhost:8090

Note: You will likely get the same warnings before running this script as above

Note: Windows may prompt about firewall access. You need to allow access for the script to work. You should select the option to allow other hosts on your network to access this service.

The script listens on port 8090. So if manually enabling a firewall for local LAN access, you want to be allowing incoming connectiosn to port 8090 on your computer.

## Configuration
* Point your browser at either http://localhost:8090 or http://[IP of computer]:8090 and you should see The banner "SolarMon" displayed with a settings cog wheel
* Click the cog wheel or browse to http://localhost:8090/admin to bring up the admin page (when prompted, login as user "admin" and password "123456789")
* Select the inverter/data source type and go from there inputing the credentials or your given device. 
   - Note: Only Solis is supported for now.
* If additionally using a Shelly EM/EM Pro, then select the grid source drop-down to enable the additional Shelly credententials
* Once you select the data sources, various fields will be shown that need to be populated with the related credentials.
* When ready to save, click the "Apply" button
* To get back to the dashboard, click the "Show Dashboard" button or separately browse to http://localhost:8090 or http://[IP of computer]:8090
* If the Shelly or inverter credentials are correct, then actual usage data should soon appear on the main dashboard.
