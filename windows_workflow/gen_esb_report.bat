SET PYTHON=python3.exe
SET HDF_DATA=hdf_data
SET ESB_HDF_SCRIPT=..\esb_hdf_reader.py
SET GEN_REPORT_SCRIPT=..\gen_report.py
SET ESB_HDF_FILE=esb_hdf.csv
SET GEN_REPORT_FILE=esb_report.xlsx
SET REPORTS=day week month year hour tariff 24h weekday

REM prepare directory for parsed HDF JSON data
IF not exist %HDF_DATA% (mkdir %HDF_DATA%)
del /s /q %HDF_DATA%\*.*

REM Read ESB HDF file and export JSONL files
%PYTHON% %ESB_HDF_SCRIPT% --file %ESB_HDF_FILE% --odir %HDF_DATA%

REM Example 24h report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report_24h.xlsx ^
    --reports %REPORTS% ^
    --tariff_rate 24h:0.4327 ^
    --tariff_interval 00-00:24h ^
    --standing_rate 0.0346 ^
    --fit_rate 0.21 


pause
