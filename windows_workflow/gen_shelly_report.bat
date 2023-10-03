SET PYTHON=python3.exe
SET SHELLY_DATA=shelly_data
SET SHELLY_SCRIPT=..\shelly_em_data_util.py
SET GEN_REPORT_SCRIPT=..\gen_report.py
SET REPORTS=day week month year hour tariff 24h weekday

REM Shelly API config
SET SHELLY_HOST=example.com
SET SHELLY_AUTH_KEY=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
SET SHELLY_DEVICE_ID=000000000000

REM prepare directory for parsed SHELLY JSON data
IF not exist %SHELLY_DATA% (mkdir %SHELLY_DATA%)

REM Retrieve data from Shelly Cloud
%PYTHON% %SHELLY_SCRIPT% ^
    --host %SHELLY_HOST% ^
    --id %SHELLY_DEVICE_ID% ^
    --auth_key %SHELLY_AUTH_KEY% ^
    --odir "%SHELLY_DATA%" ^
    --days 30 

REM Example EV report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %SHELLY_DATA% ^
    --file shelly_report_ev.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 ^
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost ^
    --standing_rate 0.0453 ^
    --fit_rate 0.21 

pause
