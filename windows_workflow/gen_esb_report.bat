SET PYTHON=python3.exe
SET HDF_DIR=hdf_files
SET HDF_DATA=hdf_data
SET ESB_HDF_SCRIPT=..\esb_hdf_reader.py
SET GEN_REPORT_SCRIPT=..\gen_report.py
SET TARIFF_PLANS=..\sample_tariffs_plan.json
SET REPORTS=day week month year hour tariff 24h weekday

REM prepare directory for parsed HDF JSON data
IF not exist %HDF_DATA% (mkdir %HDF_DATA%)
del /s /q %HDF_DATA%\*.*

REM Read ESB HDF file and export JSONL files
%PYTHON% %ESB_HDF_SCRIPT% ^
    --file %HDF_DIR% ^
    --odir %HDF_DATA%

REM Example report
%PYTHON% %GEN_REPORT_SCRIPT% ^
    --idir %HDF_DATA% ^
    --file esb_report.xlsx ^
    --reports %REPORTS% ^
    --tariffs %TARIFF_PLANS% 

pause
