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
  --hide_columns [{datetime,ts,year,month,week,day,weekday,hour,hours,tariff_name,tariff_rate,standing_rate,standing_cost,import,import_cost,solar,solar_pv1,solar_pv2,solar_pv3,solar_pv4,battery_solar_charge,battery_grid_charge,battery_charge,battery_discharge,battery_storage,battery_capacity,solar_consumed,solar_consumed_percent,solar_credit,export_rate,export,export_percent,export_credit,consumed,rel_import,savings,savings_percent,bill_amount} ...]

```
Options:
* --file /path/to/report.xlsx  
This sets where to write the generated Excel report
* --idir /path/to/input/files
This defines the directory of input JSONL files for the report.
* --start YYYYMMDD --end YYYYMMDD  
Optional start and end times for the report. If omitted, the report will span the full time period covered by the input files. These options allow for limiting the report to the days between the start and end dates. For example --start 20230607 --end 20240708 will include days between June 7th 2023 and July 8th 2024 inclusive. You may also just specify just one of these options to limit the behaviour to a specific start or end date.
* --timezone TIMEZONE  
Allows for specifying of a timezone. The default is Europe/Dublin and should be fine for any processing within Ireland the UK. 
* --currency CURRENCY   
Defines the currency symbol. This defaults to €
* --tariff_rate <name>:<value>  
This sets the tariff rates in use. Each tariff is defined by a <name>:<value> and multiple tariffs can be sepcified. For example --tariff_rate Day:0.35 Night:0.20 Peak:0.45 .. would define three tariffs Day, Night and Peak. The values specified are in whole currency units (Euro, not cent)
* --tariff_interval <[D-D:]HH-HH:Tariff Name> ..  
The tariff intervals set the optional day range (numbered 1-7) and start/end hours and mapped tariff name
  - 17-19:Peak ... 7 days a week between 5pm and 7pm, the Peak tariff applies
  - 6-7:08-23:Weekend ... Between Saturday(6) and Sunday(7), 8am-11pm, Weekend tariff applies 
* --fit_rate <value>  
This is the hourly rate for FIT specific in whole unit currency (Euro)
* --standing_rate <value>  
This option specifies the per hour standing charge in whole unit currency (Euro)
* --annual_standing_charge <value>  
This option specifies the per year standing charge in whole unit currency (Euro). This option over-rides the --standing_rate option. Internally the annual value is divided by 365*24 to render it into a per-hour value.
* --reports [{year,month,week,day,hour,tariff,weekday,24h} ...]  
This option specifies the individual sheet reports to generate andf the order in which they appear in the Excel file. Multiple reports are space separated. For example --report "day hour" will only generate the day and hour sheets and in that order. The default set of reports is "year month week day hour tariff weekday 24h".
* --hide_columns [list of columns to hide]  
This option hides a list of fields from all generated sheets. The full list of posibilities is displayed above in the usage detail. The values are space separated. Example --hide_columns "weekday standing_rate" will hide the weekday and standing rate columns in the generated sheets. These columns are still in the generated file but hidden by default.


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
* [Solis Hybrid Inverter Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/solis_hybrid_report.xlsx)
* [Solis String Inverter + Shelly Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/solis_shelly_report.xlsx)
