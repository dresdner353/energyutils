# Report Generator Utility

The report generator script generates an Excel file from a directory of YYYY-MM-DD.jsonl files. Multiple charts are inserted into the generated Excel file based on the selected reports. Each report includes a data sheet with its related numbers. Then a series of charts are inserted to graph that data. 

## Usage
```
usage: gen_report.py [-h] --file FILE --idir IDIR [--start START] [--end END]
                     [--timezone TIMEZONE] [--currency CURRENCY]
                     [--tariff_rate TARIFF_RATE [TARIFF_RATE ...]]
                     [--tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]]
                     [--fit_rate FIT_RATE] [--standing_rate STANDING_RATE]
                     [--annual_standing_charge ANNUAL_STANDING_CHARGE]
                     [--verbose]
                     [--reports [{year,month,week,day,hour,tariff,weekday,24h} ...]]

Energy Data Report Generator

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Output XLSX file
  --idir IDIR           Input Directory for data files
  --start START         Calculation Start Date (YYYYMMDD)
  --end END             Calculation End Date (YYYYMMDD)
  --timezone TIMEZONE   Timezone
  --currency CURRENCY   Currency Sumbol (def:€)
  --tariff_rate TARIFF_RATE [TARIFF_RATE ...]
                        kwh Tariff <NAME:rate/kWh> <NAME:rate/kWh> ...
  --tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]
                        Time Interval for Tariff <[D-D:]HH-HH:Tariff Name>
                        <[D-D:]HH-HH:Tariff Name> ...
  --fit_rate FIT_RATE   FIT Rate rate/kWh
  --standing_rate STANDING_RATE
                        Standing Rate (cost per hour)
  --annual_standing_charge ANNUAL_STANDING_CHARGE
                        Annual Standing Charge (cost per year)
  --verbose             Enable verbose output
  --reports [{year,month,week,day,hour,tariff,weekday,24h} ...]
                        Reports to generate
  --hide_columns [{datetime,ts,year,month,week,day,weekday,hour,hours,tariff_name,tariff_rate,standing_rate,standing_cost,import,import_cost,solar,battery_solar_charge,battery_grid_charge,battery_charge,battery_discharge,battery_storage,battery_capacity,solar_consumed,solar_consumed_percent,solar_credit,export_rate,export,export_percent,export_credit,consumed,rel_import,savings,savings_percent,bill_amount} ...]

```
Notes:
* The script is run and pointed at a directory of input files (YYYY-MM-DD.jsonl)
* The output file is the destination Excel (.xlsx) file
* Electricity tariffs can be set using the --tariff_rate option and provided multiple times per separate tariff
* Tariff intervals are defined using the --tariff_interval option that sets the optional day range (numbered 1-7), start/end hours and tariff name
  - 17-19:Peak ... 7 days a week between 5pm and 7pm, the Peak tariff applies
  - 6-7:08-23:Weekend ... Between Saturday(6) and Sunday(7), 8am-11pm, Weekend tariff applies 
* A FIT rate for microgen export may be set using the --fit_rate
* A hourly standing charge may be set via the --standing_rate option.
* Alternatively use the --annual_standing_charge option to specify the standing charge as a yearly total.
* The --reports option can be used to limit the set of generated reports to a desired subset of values. Multiple reports may be specified one after the other and in the order they should be written to the XLSX file. By default all reports are generated.
* The --start and --end options can be used to limit the report to a specific date range. The values are specified in YYYYMMDD. For example --start 20230912 will start from September 12th 2023 and --end 20240103 would end on Jan 3rd 2024. You can use either field or both depending on the desired limits.
* The --hide_columns option allows for a list of columns to be hidden in the generated file. Multiple columns can be specified by space separating the values. 


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

## Example Reports
Some examples here of the kind of data generated in the Excel files.

* [ESB Report (Import/Export Only)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/esb_report.xlsx)
* [Shelly Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/shelly_report.xlsx)
