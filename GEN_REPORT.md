# Report Generator Utility

The report generator script generates an XLSX file from a directory of YYYYMMDD.jsonl files.

THIS IS A WORK IN PROGRESS

## Usage
```
usage: gen_report.py [-h] --file FILE --idir IDIR [--tariff_rate TARIFF_RATE [TARIFF_RATE ...]]
                     [--tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]] [--fit_rate FIT_RATE]
                     [--verbose]

Energy Data Report Generator

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Output XLSX file
  --idir IDIR           Input Directory for data files
  --tariff_rate TARIFF_RATE [TARIFF_RATE ...]
                        kwh Tariff <NAME:rate/kWh> <NAME:rate/kWh> ...
  --tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]
                        Time Interval for Tariff <HH:HH:Tariff Name> <HH:HH:Tariff Name> ...
  --fit_rate FIT_RATE   FIT Rate rate/kWh
  --verbose             Enable verbose output
```
Notes:
* The script is run and pointed at a directory of input files (YYYYMMDD.jsonl)
* The output file is the destination Excell (.xlsx) file
* Electricity tariffs can be set using the --tariff_rate option and provided multiple times per separate tariff
* Tariff intervals are defined using the --tariff_interval option that sets the start and end hour and maps to the named tariff rate
* A FIT rate for microgen export may be set using the --fit_rate


## Example Run
```
python3  energyutils/gen_report.py \
             --idir Desktop/esb_data \
             --file Desktop/power_report.xlsx \
             --tariff_rate Day:0.4241 Night:0.2092 Boost:0.1228 \
             --tariff_interval 08:23:Day 23:02:Night 02:04:Boost 04:08:Night \
             --fit_rate 0.21 \
Mon May  1 16:25:57 2023 Loaded 140 files, 3311 records
Mon May  1 16:25:57 2023 Adding worksheet All (3311 records)
Mon May  1 16:25:57 2023 Adding worksheet Day (140 records)
Mon May  1 16:25:57 2023 Adding worksheet Month (5 records)
Mon May  1 16:25:57 2023 Adding worksheet Year (2 records)
Mon May  1 16:25:57 2023 Adding worksheet 24h (24 records)
Mon May  1 16:25:57 2023 Adding worksheet Tariff (4 records)
```