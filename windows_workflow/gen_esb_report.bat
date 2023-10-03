SET PYTHON=python3.exe
SET HDF_DATA=hdf_data
SET ESB_HDF_SCRIPT=..\esb_hdf_reader.py
SET GEN_REPORT_SCRIPT=..\gen_report.py
SET ESB_HDF_FILE=esb_hdf.csv
SET REPORTS=day week month year hour tariff 24h weekday

REM prepare directory for parsed HDF JSON data
IF not exist %HDF_DATA% (mkdir %HDF_DATA%)
del /s /q %HDF_DATA%\*.*

REM Read ESB HDF file and export JSONL files
%PYTHON% %ESB_HDF_SCRIPT% ^
    --file %ESB_HDF_FILE% ^
    --odir %HDF_DATA%

REM Example 24h report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_24h.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate 24h:0.4327 ^
    --tariff_interval 00-00:24h ^
    --standing_rate 0.0346 ^
    --fit_rate 0.21 


REM Example Smart report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_smart.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4310 Night:0.2265 Peak:0.4596 ^
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak ^
    --standing_rate 0.0346 ^
    --fit_rate 0.21 


REM Example EV report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_ev.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.4320 Night:0.2086 Boost:0.1225 ^
    --tariff_interval 08-23:Day 23-08:Night 02-04:Boost ^
    --standing_rate 0.0453 ^
    --fit_rate 0.21 



REM Example Complex plan with free days
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_free_sun.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate Day:0.5094 Night:0.3743 Peak:0.6223 Free:0 ^
    --tariff_interval 08-23:Day 23-08:Night 17-19:Peak 7-7:09-17:Free ^
    --standing_rate 0.0321 ^
    --fit_rate 0.21 



pause
