Steps to get your Solis inverter report generating on Microsoft Windows:

Note: This only works for people with a Solis inverter. A hybrid variant will measure 
solar and grid import/export and a string variant will measure only solar. For string inverter
owners, you may also use a Shelly EM/Pro in conjunction with the Solis inverter to source grid 
import/export data and merge with the Solis solar data

* Download Python and run initial setup
----------------------------------------------------------------------------
- Follow the Python installation and initial setup instructions in README_ESB.txt

* Get your Solis and optional Shelly Cloud API credentials
----------------------------------------------------------------------------
Right-click on the gen_solis_report.bat file and select edit. 

Locate the following sections in the file.. 

REM Solis API config
SET SOLIS_API_HOST=https://www.soliscloud.com:PPPPP
SET SOLIS_KEY_ID=XXXXXXXXXXXXXXXXXXX
SET SOLIS_KEY_SECRET=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
SET SOLIS_INVERTER_SN=ZZZZZZZZZZZZZZZZ
SET SOLIS_STRINGS=0

REM Shelly API config
SET SHELLY_API_HOST=example.com
SET SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SET SHELLY_DEVICE_ID=000000000000

You will need to update these details with credential data from your Solis and optional Shelly Cloud account: 

Solis Cloud API Instructions:
* Go to the Solis support site https://solis-service.solisinverters.com/en/support/home
* Sign in or register for an account
* Select the option to submit a new ticket
* Enter your product type, name, model etc and set the Ticket Type to API Access Request
* You also provide the email address you use to sign into your Solis account
* In the brief description, mention that you wish to get API access enabled
* Solis should typically turn this request around in around 1 day and will email you instructions 
  on how to then setup the API access on your account.
* Copy the API URL to the SOLIS_API_HOST field with no trailling "/"
* Copy the KeyID to the SOLIS_KEY_ID field
* Copy the KeySecret to the SOLIS_KEY_SECRET field
* Get your inverter serial number from your web login or inverter app 
  and copy it to the SOLIS_INVERTER_SN field
* You can optionally set the SOLIS_STRINGS field to 1, 2, 3, etc to represent the number of strings you have in your setup. 
  Leave set to 0 if you only want to see the total sdolar generated and no per-string separation

In the end, these four lines might look something like this...

SET SOLIS_API_HOST=https://www.soliscloud.com:13333
SET SOLIS_KEY_ID=1355555555676955555
SET SOLIS_KEY_SECRET=4dddddddd1ee46bcccccc182aaaaa5f4
SET SOLIS_INVERTER_SN=155555555A055555
SET SOLIS_STRINGS=2

Save the file with your edits.

Shelly Cloud API Instructions (only for Solis string inverters + Shelly EM):
Note: skip this entirely if you have a Solis Hybrid inverter
* Sign into control.shelly.cloud using your account credentials
* Navigate to Settings -> User Settings -> Access And Permissions -> Authorization Cloud Key and click Get
* This will display two pieces of information:
   - Server: https://shelly-xx.eu.shelly.cloud
   - The cloud key (a long sequence of letters and digits)
* Ignore the https:// prefix and copy the server part (e.g. shelly-xx.eu.shelly.cloud) and paste over the example.com text above
* Copy the cloud key and replace the ZZZZZZZZZZZZZ above
* Go to your Shelly EM device on the account and navigate to settings -> Device information
* Copy the "Device Id" value and paste over the 000000000000 above
* Remove the "REM" comment on the three SHELLY options on the script call

In the end, these three lines will look something like this...

SET SHELLY_HOST=shelly-99.eu.shelly.cloud
SET SHELLY_AUTH_KEY=bj3ex4005yfake8yy2k6sfakeun8fakeimrfaketyzffakebblmfakencyqfakeq2spfakeBCDEFFAKEKLMNOPQRSTUV
SET SHELLY_DEVICE_ID=555fakec4d55


* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, double-click on "gen_solis_report". This should retrieve data from the 
Solis Cloud API and then generate report files in the same directory. 

Note: Be aware that each Solis API call uses a delay of 3 seconds. So it may take some time 
to pull the initial 30 days of information. However this data is stored permanently such 
that later invokes of the script will only retrieve new files and should take less time.

You can customise the --days option on the script call to pull back a larger backlog of files

* Customise the Report pricing detail
----------------------------------------------------------------------------
This "gen_solis_report" script performs two functions:
* Downloads data from Solis Cloud
* Generates the Excel file report

Part of the script includes the ability to set pricing details:

REM Example EV report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %SOLIS_DATA% ^
    --file solis_report_ev.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 ^
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost ^
    --annual_standing_charge 303 ^
    --fit_rate 0.21 

The --tariff_rate and --tariff_interval options designate the tariffs in use and the time periods that they apply. 
The --annual_standing_charge option specifies the annual standing charge for your plan. 

See https://github.com/dresdner353/energyutils/blob/main/GEN_REPORT.md for full options on this report generator
