# ESB HDF Reader

The Electricity Supply Board in Ireland have a data download service available to customers with smart meters. They refer to this data as their harmonised data format. It's essentially power import and export data provided in 30-minute intervals and downloaded in CSV files. It has been an awkward data source in general as the power usage values are timestamped n local time when the usage period ended and also need to be summed up per hour and divided by 2 to get real kWh values.

The ```esb_hdf_reader.py``` script can be used to parse this data into a more analytics or spreadsheet-friendly form. 

## Usage
```
usage: esb_hdf_reader.py [-h] --file FILE --odir ODIR [--start START] [--end END] [--timezone TIMEZONE]
                         [--tariff_rate TARIFF_RATE [TARIFF_RATE ...]]
                         [--tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]] [--fit_rate FIT_RATE]
                         [--decimal_places DECIMAL_PLACES] [--verbose]

ESB HDF Reader

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           ESB HDF file
  --odir ODIR           Output Directory
  --start START         Calculation Start Date (YYYYMMDD)
  --end END             Calculation End Date (YYYYMMDD)
  --timezone TIMEZONE   Timezone
  --tariff_rate TARIFF_RATE [TARIFF_RATE ...]
                        kwh Tariff <NAME:rate/kWh> <NAME:rate/kWh> ...
  --tariff_interval TARIFF_INTERVAL [TARIFF_INTERVAL ...]
                        Time Interval for Tariff <HH:HH:Tariff Name> <HH:HH:Tariff Name> ...
  --fit_rate FIT_RATE   FIT Rate rate/kWh
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:3)
  --verbose             Enable verbose output
```

Notes:
* The script is run and pointed as a HDF file as downloaded from the ESB (--file file.csv)
* The output directory is set to control where the script dumps all generated files (--odir <dir>)
* The start and end dates (--start/--end) may be optionally set narrow the aggregation to a specific billing period. The days are fully inclusive (from 00:00 on start day to 23:59 on end day)
* Timezone can be asserted with the --timezone option. By default, this is set to Europe/Dublin. The ESB HDF data comes in local Europe/Dublin timezone. So this option should not be required.
* Electricity tariffs can be set using the --tariff_rate option and provided multiple times per separate tariff
* Tariff intervals are defined using the --tariff_interval option that sets the start and end hour and maps to the named tariff rate
* A FIT rate for solar export may be set using the --fit_rate
* Decimal places can be controlled using the --decimal_places option and this defaults to 3 


## Example Call (using the included example file)
```
python3 energyutils/esb_hdf_reader.py \
            --file energyutils/HDF_example.csv \
            --tariff_rate Day:0.4241 Night:0.2092 Boost:0.1228 \
            --tariff_interval 08:23:Day 23:02:Night 02:04:Boost 04:08:Night \
            --start 20230301 \
            --end 20230328 \
            --fit_rate 0.21 \
            --odir Desktop/Reports

Sun Apr 23 15:39:58 2023 Parsed 3125 hourly records from /Users/cormac/work/energyutils/HDF_example.csv
Sun Apr 23 15:39:58 2023 Cost Calculation between 2023-03-01T00:00:00+00:00 <--> 2023-03-28T23:59:59+01:00
Sun Apr 23 15:39:58 2023 Writing tariff data to Desktop/Reports/HDF_example_tariff.jsonl
Sun Apr 23 15:39:58 2023 Writing tariff data to Desktop/Reports/HDF_example_tariff.csv
Sun Apr 23 15:39:58 2023 Writing all data to Desktop/Reports/HDF_example_all.jsonl
Sun Apr 23 15:39:58 2023 Writing all data to Desktop/Reports/HDF_example_all.csv
Sun Apr 23 15:39:58 2023 Writing year data to Desktop/Reports/HDF_example_year.jsonl
Sun Apr 23 15:39:58 2023 Writing year data to Desktop/Reports/HDF_example_year.csv
Sun Apr 23 15:39:58 2023 Writing month data to Desktop/Reports/HDF_example_month.jsonl
Sun Apr 23 15:39:58 2023 Writing month data to Desktop/Reports/HDF_example_month.csv
Sun Apr 23 15:39:58 2023 Writing day data to Desktop/Reports/HDF_example_day.jsonl
Sun Apr 23 15:39:58 2023 Writing day data to Desktop/Reports/HDF_example_day.csv
Sun Apr 23 15:39:58 2023 Writing hour data to Desktop/Reports/HDF_example_hour.jsonl
Sun Apr 23 15:39:58 2023 Writing hour data to Desktop/Reports/HDF_example_hour.csv
```

## Tariff Output Files
These files detail the total usage and costs/credit for the defined tariffs. If you have specified a FIT rate, that will appear in this file. You get two formats for the same output, one JSONL and one CSV.

JSON:
```json
{"tariff": "Boost", "rate": 0.1228, "import": 22.3945, "import_cost": 2.7500, "export": 0, "export_credit": 0}
{"tariff": "Day", "rate": 0.4241, "import": 288.6415, "import_cost": 122.4129, "export": 0, "export_credit": 0}
{"tariff": "FIT", "rate": 0.2100, "import": 0, "import_cost": 0, "export": 0, "export_credit": 0}
{"tariff": "Night", "rate": 0.2092, "import": 74.4965, "import_cost": 15.5847, "export": 0, "export_credit": 0}
```

CSV:
```
export,export_credit,import,import_cost,rate,tariff
0,0,22.395,2.75,0.123,Boost
0,0,288.641,122.413,0.424,Day
0,0,0,0,0.21,FIT
0,0,74.496,15.585,0.209,Night
```

| export | export_credit | import  | import_cost | rate  | tariff |
|--------|---------------|---------|-------------|-------|--------|
| 0      | 0             | 22.395  | 2.75        | 0.123 | Boost  |
| 0      | 0             | 288.641 | 122.413     | 0.424 | Day    |
| 0      | 0             | 0       | 0           | 0.21  | FIT    |
| 0      | 0             | 74.496  | 15.585      | 0.209 | Night  |
