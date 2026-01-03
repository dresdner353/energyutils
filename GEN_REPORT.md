# Report Generator Utility

The report generator script generates an Excel file from a directory of YYYY-MM-DD.jsonl files. Multiple charts are inserted into the generated Excel file based on the selected reports. Each report includes a data sheet with its related numbers. Then a series of charts are inserted to graph that data. 

## Usage
```
usage: gen_report.py [-h] --file FILE --tariffs TARIFFS --idir IDIR [--start START]
                     [--end END] [--timezone TIMEZONE] [--currency CURRENCY]
                     [--verbose]
                     [--reports [{year,month,week,day,hour,tariff,weekday,24h} ...]]
                     [--hide_columns [{datetime,ts,year,month,week,day,weekday,hour,hours,plan,tariff_name,tariff_rate,standing_rate,standing_cost,import,import_cost,grid_voltage_min,grid_voltage_1_min,grid_voltage_2_min,grid_voltage_3_min,grid_voltage_max,grid_voltage_1_max,grid_voltage_2_max,grid_voltage_3_max,solar,solar_pv1,solar_pv2,solar_pv3,solar_pv4,battery_solar_charge,battery_grid_charge,battery_charge,battery_discharge,battery_storage,battery_capacity,battery_cycles,solar_consumed,solar_consumed_percent,solar_credit,export_rate,export,export_percent,export_credit,consumed,savings,savings_percent,bill_amount} ...]]

Energy Data Report Generator

options:
  -h, --help            show this help message and exit
  --file FILE           Output XLSX file
  --tariffs TARIFFS     Tariffs JSON file
  --idir IDIR           Input Directory for data files
  --start START         Calculation Start Date (YYYYMMDD)
  --end END             Calculation End Date (YYYYMMDD)
  --timezone TIMEZONE   Timezone
  --currency CURRENCY   Currency Symbol (def:€)
  --verbose             Enable verbose output
  --reports [{year,month,week,day,hour,tariff,weekday,24h} ...]
                        Reports to generate
  --hide_columns [{datetime,ts,year,month,week,day,weekday,hour,hours,plan,tariff_name,tariff_rate,standing_rate,standing_cost,import,import_cost,grid_voltage_min,grid_voltage_1_min,grid_voltage_2_min,grid_voltage_3_min,grid_voltage_max,grid_voltage_1_max,grid_voltage_2_max,grid_voltage_3_max,solar,solar_pv1,solar_pv2,solar_pv3,solar_pv4,battery_solar_charge,battery_grid_charge,battery_charge,battery_discharge,battery_storage,battery_capacity,battery_cycles,solar_consumed,solar_consumed_percent,solar_credit,export_rate,export,export_percent,export_credit,consumed,savings,savings_percent,bill_amount} ...]
                        columns to hide
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
* --tariffs <file.json>
Specifies one or more tariff plans defined in a JSON file. See [Tariff Plan File Example](./sample_tariffs_plan.json) and further details below.
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
             --idir my_data \
             --file report.xlsx \
             --tariffs sample_tariffs_plan.json 
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

## Tariff Plan File Example

```json
[
    {
        "name": "Sample Smart Plan",
        "start": "2000-01-01",
        "end": "2030-12-31",
        "annual_standing_charge": 250.77,
        "fit_rate": 0.195,
        "tariffs": [
            {
                "name": "Day",
                "start": 0,
                "end": 23,
                "rate": 0.2814
            },
            {
                "name": "Night",
                "start": 23,
                "end": 8,
                "rate": 0.1479
            },
            {
                "name": "Peak",
                "start": 17,
                "end": 19,
                "rate": 0.3002
            },
            {
                "name": "Sat/Sun Free",
                "days": [6,7],
                "start": 08,
                "end": 17,
                "rate": 0.0
            }
        ]
    }
]
```
Notes:
* The outer JSON structure is a list of tariff plans. 
Each plan is an object with fields as described below.
* The "start" and "end" fields in the plan define the date range for which the plan is valid.
These are in YYYY-MM-DD format and should be inclusive for any dates covered by the input data. The purpose of these fields is to allow for multiple plans to be defined in the same file for different time periods, new plans added over time when the tariff changes. The plan selected for any given day is based on first plan that is matched to the given day. Ideally the plans should be set with the corect start and end times to guarantee no overlaps. Best advised to place then in chronological order.
* The "annual_standing_charge" field defines the yearly fixed standing charge for the plan. 
Each hour will have a per hour cost applied. (after dividing by /365/24)
* The "fit_rate" field defines the feed-in-tariff rate for any exported solar energy.
* The "tariffs" field is a list of tariff objects. Each tariff object defines a name, start and end hour (0-23) and the rate per kWh for that tariff
* An optional "days" field may be specified in a tariff object. 
This is a list of week days (1=Monday to 7=Sunday) for which the specific tariff applies. If omitted, the tariff applies to all days. This allows for weekend or specific day tariffs to be defined. In the above example, the "Sat/Sun Free" tariff applies only on Saturdays and Sundays between 8am and 5pm. 
* Tariffs are populated in list order when parsed.
This means that an earlier tariff may define a price for all hours in a day and a later tariff may override specific hours or days. Therefore it is important to order the tariffs correctly to ensure the desired behaviour. In the above example, the "Day" tariff applies to all hours except those overridden by the "Night", "Peak" and "Sat/Sun Free" tariffs.

## Example Reports
Some examples here of the kind of data generated in the Excel files.

* [ESB Report (Import/Export Only)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/esb_report.xlsx)
* [Shelly Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/shelly_report.xlsx)
* [Solis Hybrid Inverter Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/solis_hybrid_report.xlsx)
* [Solis String Inverter + Shelly Report (Import, Export & Solar)](https://github.com/dresdner353/energyutils/raw/main/sample_reports/solis_shelly_report.xlsx)
