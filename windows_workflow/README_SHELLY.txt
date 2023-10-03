Steps to get your Shelly EM report generating on Microsoft Windows:

Note: This only works for people with a Shelly EM or pro variant energy monitor
installed in their home. It should have 2 CT clamps fitted. The first on the mains 
feed into the house and the second clamp on the output feed from the solar PV 
inverter. Its not really suitable for owners of hybrid inverters as the inverter 
output feed is a mix of solar and battery power.

* Download Python and run initial setup
----------------------------------------------------------------------------
- Follow the Python installation and initial setup instructions in README_ESB.txt

* Get you Shelly Cloud API credentials
----------------------------------------------------------------------------
Right-click on the gen_shelly_report.bat file and select edit. 

Locate the following section in the file.. 

REM Shelly API config
SET SHELLY_HOST=example.com
SET SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SET SHELLY_DEVICE_ID=000000000000

You will need to update these details with credential data from your Shelly Cloud account. 

* Sign into control.shelly.cloud using your account credentials
* Navigate to Settings -> User Settings -> Access And Permissions -> Authorization Cloud Key and click Get
* This will display two pieces of information:
   - Server: https://shelly-xx.eu.shelly.cloud
   - The cloud key (a long sequence of letters and digits)
* Ignore the https:// prefix and copy the server part (e.g. shelly-xx.eu.shelly.cloud) and paste over the example.com text above
* Copy the cloud key and replace the ZZZZZZZZZZZZZ above
* Go to your Shelly EM device on the account and navigate to settings -> Device information
* Copy the "Device Id" value and paste over the 000000000000 above

In the end, these three lines will look something like this...

SET SHELLY_HOST=shelly-99.eu.shelly.cloud
SET SHELLY_AUTH_KEY=bj3ex4005yfake8yy2k6sfakeun8fakeimrfaketyzffakebblmfakencyqfakeq2spfakeBCDEFFAKEKLMNOPQRSTUV
SET SHELLY_DEVICE_ID=555fakec4d55


* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, double-click on "gen_shelly_report". This should retrieve data from the 
Shelly Cloud API and then generate report files in the same directory 

* Customise the Report pricing detail
----------------------------------------------------------------------------
Follow the detailed in README_ESB.txt on how to customise the report and pricing details
