SET PYTHON=python3.exe
SET SOLIS_DATA=solis_data
SET SOLIS_SCRIPT=..\solis_data_util.py
SET GEN_REPORT_SCRIPT=..\gen_report.py
SET REPORTS=day week month year hour tariff 24h weekday

REM Solis API config
SET SOLIS_API_HOST=https://www.soliscloud.com:PPPPP
SET SOLIS_KEY_ID=XXXXXXXXXXXXXXXXXXX
SET SOLIS_KEY_SECRET=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
SET SOLIS_INVERTER_SN=ZZZZZZZZZZZZZZZZ

REM Shelly API config
REM Note: uncomment shelly_xxxxx lines below if using
REM a Shelly device in conjunction with the Solis inverter
SET SHELLY_API_HOST=example.com
SET SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SET SHELLY_DEVICE_ID=000000000000

REM prepare directory for parsed SOLIS JSON data
IF not exist %SOLIS_DATA% (mkdir %SOLIS_DATA%)

REM Retrieve data from Shelly Cloud
%PYTHON% %SOLIS_SCRIPT% ^
    --odir "%SOLIS_DATA%" ^
    --days 30 ^
    --solis_api_host %SOLIS_API_HOST% ^
    --solis_key_id %SOLIS_KEY_ID% ^
    --solis_key_secret %SOLIS_KEY_SECRET%  ^
    --solis_inverter_sn %SOLIS_INVERTER_SN% ^
REM    --shelly_api_host %SHELLY_API_HOST% ^
REM    --shelly_device_id %SHELLY_DEVICE_ID% ^
REM    --shelly_auth_key %SHELLY_AUTH_KEY% ^

REM Example EV report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %SOLIS_DATA% ^
    --file solis_report_ev.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 ^
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost ^
    --annual_standing_charge 303 ^
    --fit_rate 0.21 

pause
