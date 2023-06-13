# Report Generator Utility

The report generator script generates an XLSX file from a directory of YYYY-MM-DD.jsonl files.

## Usage
```
usage: gen_report.py [-h] --file FILE --idir IDIR [--start START] [--end END]
                     [--timezone TIMEZONE]
                     [--tariff_rate TARIFF_RATE [TARIFF_RATE ...]]
                     [--tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]]
                     [--fit_rate FIT_RATE] [--standing_rate STANDING_RATE]
                     [--verbose]

Energy Data Report Generator

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Output XLSX file
  --idir IDIR           Input Directory for data files
  --start START         Calculation Start Date (YYYYMMDD)
  --end END             Calculation End Date (YYYYMMDD)
  --timezone TIMEZONE   Timezone
  --tariff_rate TARIFF_RATE [TARIFF_RATE ...]
                        kwh Tariff <NAME:rate/kWh> <NAME:rate/kWh> ...
  --tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]
                        Time Interval for Tariff <[D-D:]HH-HH:Tariff Name>
                        <[D-D:]HH-HH:Tariff Name> ...
  --fit_rate FIT_RATE   FIT Rate rate/kWh
  --standing_rate STANDING_RATE
                        Standing Charge (cost per hour)
  --verbose             Enable verbose output
```
Notes:
* The script is run and pointed at a directory of input files (YYYYMMDD.jsonl)
* The output file is the destination Excel (.xlsx) file
* Electricity tariffs can be set using the --tariff_rate option and provided multiple times per separate tariff
* Tariff intervals are defined using the --tariff_interval option that sets the optional day range (numbered 1-7), start/end hours and tariff name
  - 17-19:Peak ... 7 days a week between 5pm and 7pm, the Peak tariff applies
  - 6-7:08-23:Weekend ... Between Saturday(6) and Sunday(7), 8am-11pm, Weekend tariff applies 
* A FIT rate for microgen export may be set using the --fit_rate
* A standing charge may be set via the --standing_rate option. Note however that this value is the cost per hour. So divide any annual or monthly values accordingly to get the per hour equivalent.


## Example Run
```
# Three tariffs... Day (0.4750), Night (0.4750) and Free (0)
# Day applies 8am to 11pm and Night is 11pm to 8am
# However on Saturdays (day 6), 8-11pm is free
# FIT rate for exported solar is 0.21/kWh

python3  energyutils/gen_report.py \
             --idir cl_esb \
             --file cl_esb_report_sat_free.xlsx \
             --tariff_rate Day:0.4750 Night:0.4750 Free:0 \
             --tariff_interval 08-23:Day 23-08:Night 6-6:08-23:Free \
             --standing_rate 0.0346 \
             --fit_rate 0.21 
Sun Jun  4 23:00:47 2023 Loaded 177 files, 4209 records
Sun Jun  4 23:00:47 2023 Adding worksheet Hour (4209 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Day (177 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Week (27 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Month (7 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Year (2 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Weekday (7 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet 24h (24 rows)
Sun Jun  4 23:00:47 2023 Adding worksheet Tariff (3 rows)

```
