Steps to get your Solis inverter report generating on Mac/Linux:

Note: This only works for people with a Solis inverter. A hybrid variant will measure 
solar and grid import/export and a string variant will measure only solar. For string inverter
owners, you may also use a Shelly EM/Pro in conjunction with the Solis inverter to source grid 
import/export data and merge with the Solis solar data

* Download Python and run initial setup
----------------------------------------------------------------------------
- Follow the Python installation and initial setup instructions in README_ESB.txt

* Get your Solis and optional Shelly Cloud API credentials
----------------------------------------------------------------------------
Edit gen_solis_report.sh file 

Locate the following section in the file.. 

# Solis API
SOLIS_API_HOST=https://www.soliscloud.com:PPPPP
SOLIS_KEY_ID=XXXXXXXXXXXXXXXXXXX
SOLIS_KEY_SECRET=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
SOLIS_INVERTER_SN=ZZZZZZZZZZZZZZZZ

# Shelly API config
# Note: uncomment shelly_xxxxx lines below if using
# a Shelly device in conjunction with the Solis inverter
SHELLY_API_HOST=example.com
SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SHELLY_DEVICE_ID=000000000000

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
  and copy it to te SOLIS_INVERTER_SN field

In the end, these four lines will look something like this...

SOLIS_API_HOST=https://www.soliscloud.com:13333
SOLIS_KEY_ID=1355555555676955555
SOLIS_KEY_SECRET=4dddddddd1ee46bcccccc182aaaaa5f4
SOLIS_INVERTER_SN=155555555A055555

Shelly Cloud API Instructions (optional):
* Sign into control.shelly.cloud using your account credentials
* Navigate to Settings -> User Settings -> Access And Permissions -> Authorization Cloud Key and click Get
* This will display two pieces of information:
   - Server: https://shelly-xx.eu.shelly.cloud
   - The cloud key (a long sequence of letters and digits)
* Ignore the https:// prefix and copy the server part (e.g. shelly-xx.eu.shelly.cloud) and paste over the example.com text above
* Copy the cloud key and replace the ZZZZZZZZZZZZZ above
* Go to your Shelly EM device on the account and navigate to settings -> Device information
* Copy the "Device Id" value and paste over the 000000000000 above
* Remove the "#" comment on the three SHELLY options on the script call

In the end, these three lines will look something like this...

SHELLY_HOST=shelly-99.eu.shelly.cloud
SHELLY_AUTH_KEY=bj3ex4005yfake8yy2k6sfakeun8fakeimrfaketyzffakebblmfakencyqfakeq2spfakeBCDEFFAKEKLMNOPQRSTUV
SHELLY_DEVICE_ID=555fakec4d55

* Run the Report Generation Script
----------------------------------------------------------------------------
In this folder, run "gen_solis_report.sh". This should retrieve data from the 
Shelly Cloud API and then generate report files in the same directory 

* Customise the Report pricing detail
----------------------------------------------------------------------------
Follow the detailed in README_ESB.txt on how to customise the report and pricing details
