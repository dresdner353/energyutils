# ESB HDF Reader

The Electricity Supply Board in Ireland have a data download service available to customers with smart meters. They refer to this data as their harmonised data format. It's essentially power import and export data provided in 30-minute intervals and downloaded in CSV files. It has been an awkward data source in general as the power usage values are timestamped in local time when the usage period ended and also need to be summed up per half-hour and divided by 2 to get real kWh values.

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
* The script is run and pointed at a HDF file as downloaded from the ESB (--file file.csv)
* The output directory is set to control where the script dumps all generated JSONL and CSV files (--odir <dir>)
* The start and end dates (--start/--end) may be optionally set to narrow the aggregation to a specific time/billing period. The days are fully inclusive (from 00:00 on the start day to 23:59 on the end day)
* Timezone can be asserted with the --timezone option. By default, this is set to Europe/Dublin. The ESB HDF data comes in local Europe/Dublin timezone. So this option should not be required.
* Electricity tariffs can be set using the --tariff_rate option and provided multiple times per separate tariff
* Tariff intervals are defined using the --tariff_interval option that sets the start and end hour and maps to the named tariff rate
* A FIT rate for microgen export may be set using the --fit_rate
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

## All Data Files (HDF_example_all.*)
The all data file shows the lowest granularity of usage and costs/credit combined per hour. These are the only output files that are NOT filtered by the start/end script options. So whatever is in the HDF file will end up in the all data files regardless.

The "ts" field here is an EPOCH timestamp (seconds since 1/1/1970 UTC). You also have a "datetime" field which is a "YYYY/MM/DD HH:MM:SS" format string in local time. This time represents the start of the hour being represented. So the very first row shown below is the usage during 11pm local time on that specific day. 

Each row/record also has a number of pivot/friendly fields that help with quick filtering of data:
* tariff_name
* hour
* month
* year

JSONL:
```json
{"ts": 1670540400, "datetime": "2022/12/08 23:00:00", "import": 0.3725, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.0779, "export_credit": 0, "hour": 23, "day": "20221208", "month": "202212", "year": "2022"}
{"ts": 1670544000, "datetime": "2022/12/09 00:00:00", "import": 0.4205, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.0880, "export_credit": 0, "hour": 0, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670547600, "datetime": "2022/12/09 01:00:00", "import": 0.8705, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.1821, "export_credit": 0, "hour": 1, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670551200, "datetime": "2022/12/09 02:00:00", "import": 0.2310, "export": 0, "tariff_name": "Boost", "tariff_rate": 0.1228, "import_cost": 0.0284, "export_credit": 0, "hour": 2, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670554800, "datetime": "2022/12/09 03:00:00", "import": 0.2295, "export": 0, "tariff_name": "Boost", "tariff_rate": 0.1228, "import_cost": 0.0282, "export_credit": 0, "hour": 3, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670558400, "datetime": "2022/12/09 04:00:00", "import": 0.2645, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.0553, "export_credit": 0, "hour": 4, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670562000, "datetime": "2022/12/09 05:00:00", "import": 0.2680, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.0561, "export_credit": 0, "hour": 5, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670565600, "datetime": "2022/12/09 06:00:00", "import": 0.2635, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.0551, "export_credit": 0, "hour": 6, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670569200, "datetime": "2022/12/09 07:00:00", "import": 0.6190, "export": 0, "tariff_name": "Night", "tariff_rate": 0.2092, "import_cost": 0.1295, "export_credit": 0, "hour": 7, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670572800, "datetime": "2022/12/09 08:00:00", "import": 0.7455, "export": 0, "tariff_name": "Day", "tariff_rate": 0.4241, "import_cost": 0.3162, "export_credit": 0, "hour": 8, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670576400, "datetime": "2022/12/09 09:00:00", "import": 0.5595, "export": 0, "tariff_name": "Day", "tariff_rate": 0.4241, "import_cost": 0.2373, "export_credit": 0, "hour": 9, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670580000, "datetime": "2022/12/09 10:00:00", "import": 1.3815, "export": 0, "tariff_name": "Day", "tariff_rate": 0.4241, "import_cost": 0.5859, "export_credit": 0, "hour": 10, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670583600, "datetime": "2022/12/09 11:00:00", "import": 0.9605, "export": 0, "tariff_name": "Day", "tariff_rate": 0.4241, "import_cost": 0.4073, "export_credit": 0, "hour": 11, "day": "20221209", "month": "202212", "year": "2022"}
{"ts": 1670587200, "datetime": "2022/12/09 12:00:00", "import": 0.8595, "export": 0, "tariff_name": "Day", "tariff_rate": 0.4241, "import_cost": 0.3645, "export_credit": 0, "hour": 12, "day": "20221209", "month": "202212", "year": "2022"}
```

CSV:
```
datetime,day,export,export_credit,hour,import,import_cost,month,tariff_name,tariff_rate,ts,year
2022/12/08 23:00:00,20221208,0,0,23,0.372,0.078,202212,Night,0.209,1670540400,2022
2022/12/09 00:00:00,20221209,0,0,0,0.42,0.088,202212,Night,0.209,1670544000,2022
2022/12/09 01:00:00,20221209,0,0,1,0.87,0.182,202212,Night,0.209,1670547600,2022
2022/12/09 02:00:00,20221209,0,0,2,0.231,0.028,202212,Boost,0.123,1670551200,2022
2022/12/09 03:00:00,20221209,0,0,3,0.23,0.028,202212,Boost,0.123,1670554800,2022
2022/12/09 04:00:00,20221209,0,0,4,0.265,0.055,202212,Night,0.209,1670558400,2022
2022/12/09 05:00:00,20221209,0,0,5,0.268,0.056,202212,Night,0.209,1670562000,2022
2022/12/09 06:00:00,20221209,0,0,6,0.263,0.055,202212,Night,0.209,1670565600,2022
2022/12/09 07:00:00,20221209,0,0,7,0.619,0.129,202212,Night,0.209,1670569200,2022
2022/12/09 08:00:00,20221209,0,0,8,0.746,0.316,202212,Day,0.424,1670572800,2022
2022/12/09 09:00:00,20221209,0,0,9,0.559,0.237,202212,Day,0.424,1670576400,2022
2022/12/09 10:00:00,20221209,0,0,10,1.381,0.586,202212,Day,0.424,1670580000,2022
2022/12/09 11:00:00,20221209,0,0,11,0.961,0.407,202212,Day,0.424,1670583600,2022
2022/12/09 12:00:00,20221209,0,0,12,0.86,0.365,202212,Day,0.424,1670587200,2022
2022/12/09 13:00:00,20221209,0,0,13,0.7,0.297,202212,Day,0.424,1670590800,2022
2022/12/09 14:00:00,20221209,0,0,14,0.663,0.281,202212,Day,0.424,1670594400,2022
2022/12/09 15:00:00,20221209,0,0,15,0.907,0.385,202212,Day,0.424,1670598000,2022
2022/12/09 16:00:00,20221209,0,0,16,0.81,0.344,202212,Day,0.424,1670601600,2022
2022/12/09 17:00:00,20221209,0,0,17,0.782,0.332,202212,Day,0.424,1670605200,2022
2022/12/09 18:00:00,20221209,0,0,18,0.746,0.317,202212,Day,0.424,1670608800,2022
2022/12/09 19:00:00,20221209,0,0,19,0.873,0.37,202212,Day,0.424,1670612400,2022
2022/12/09 20:00:00,20221209,0,0,20,0.746,0.316,202212,Day,0.424,1670616000,2022
2022/12/09 21:00:00,20221209,0,0,21,0.741,0.314,202212,Day,0.424,1670619600,2022
2022/12/09 22:00:00,20221209,0,0,22,0.693,0.294,202212,Day,0.424,1670623200,2022
2022/12/09 23:00:00,20221209,0,0,23,0.689,0.144,202212,Night,0.209,1670626800,2022
2022/12/10 00:00:00,20221210,0,0,0,0.601,0.126,202212,Night,0.209,1670630400,2022
2022/12/10 01:00:00,20221210,0,0,1,0.649,0.136,202212,Night,0.209,1670634000,2022
2022/12/10 02:00:00,20221210,0,0,2,0.55,0.068,202212,Boost,0.123,1670637600,2022
2022/12/10 03:00:00,20221210,0,0,3,0.488,0.06,202212,Boost,0.123,1670641200,2022
2022/12/10 04:00:00,20221210,0,0,4,0.277,0.058,202212,Night,0.209,1670644800,2022
2022/12/10 05:00:00,20221210,0,0,5,0.254,0.053,202212,Night,0.209,1670648400,2022
2022/12/10 06:00:00,20221210,0,0,6,0.295,0.062,202212,Night,0.209,1670652000,2022
2022/12/10 07:00:00,20221210,0,0,7,0.393,0.082,202212,Night,0.209,1670655600,2022
2022/12/10 08:00:00,20221210,0,0,8,0.603,0.256,202212,Day,0.424,1670659200,2022
2022/12/10 09:00:00,20221210,0,0,9,0.465,0.197,202212,Day,0.424,1670662800,2022
2022/12/10 10:00:00,20221210,0,0,10,1.187,0.503,202212,Day,0.424,1670666400,2022
2022/12/10 11:00:00,20221210,0,0,11,1.895,0.804,202212,Day,0.424,1670670000,2022
2022/12/10 12:00:00,20221210,0,0,12,1.245,0.528,202212,Day,0.424,1670673600,2022
```

Spreadsheet view of this CSV:
2022/12/09 10:00:00,20221209,0,0,10,1.381,0.586,202212,Day,0.424,1670580000,2022
2022/12/09 11:00:00,20221209,0,0,11,0.961,0.407,202212,Day,0.424,1670583600,2022
2022/12/09 12:00:00,20221209,0,0,12,0.86,0.365,202212,Day,0.424,1670587200,2022
2022/12/09 13:00:00,20221209,0,0,13,0.7,0.297,202212,Day,0.424,1670590800,2022
2022/12/09 14:00:00,20221209,0,0,14,0.663,0.281,202212,Day,0.424,1670594400,2022
2022/12/09 15:00:00,20221209,0,0,15,0.907,0.385,202212,Day,0.424,1670598000,2022
2022/12/09 16:00:00,20221209,0,0,16,0.81,0.344,202212,Day,0.424,1670601600,2022
2022/12/09 17:00:00,20221209,0,0,17,0.782,0.332,202212,Day,0.424,1670605200,2022
2022/12/09 18:00:00,20221209,0,0,18,0.746,0.317,202212,Day,0.424,1670608800,2022
2022/12/09 19:00:00,20221209,0,0,19,0.873,0.37,202212,Day,0.424,1670612400,2022
2022/12/09 20:00:00,20221209,0,0,20,0.746,0.316,202212,Day,0.424,1670616000,2022
2022/12/09 21:00:00,20221209,0,0,21,0.741,0.314,202212,Day,0.424,1670619600,2022
2022/12/09 22:00:00,20221209,0,0,22,0.693,0.294,202212,Day,0.424,1670623200,2022
2022/12/09 23:00:00,20221209,0,0,23,0.689,0.144,202212,Night,0.209,1670626800,2022
2022/12/10 00:00:00,20221210,0,0,0,0.601,0.126,202212,Night,0.209,1670630400,2022
2022/12/10 01:00:00,20221210,0,0,1,0.649,0.136,202212,Night,0.209,1670634000,2022
2022/12/10 02:00:00,20221210,0,0,2,0.55,0.068,202212,Boost,0.123,1670637600,2022
2022/12/10 03:00:00,20221210,0,0,3,0.488,0.06,202212,Boost,0.123,1670641200,2022
2022/12/10 04:00:00,20221210,0,0,4,0.277,0.058,202212,Night,0.209,1670644800,2022
2022/12/10 05:00:00,20221210,0,0,5,0.254,0.053,202212,Night,0.209,1670648400,2022
2022/12/10 06:00:00,20221210,0,0,6,0.295,0.062,202212,Night,0.209,1670652000,2022
2022/12/10 07:00:00,20221210,0,0,7,0.393,0.082,202212,Night,0.209,1670655600,2022
2022/12/10 08:00:00,20221210,0,0,8,0.603,0.256,202212,Day,0.424,1670659200,2022
2022/12/10 09:00:00,20221210,0,0,9,0.465,0.197,202212,Day,0.424,1670662800,2022
2022/12/10 10:00:00,20221210,0,0,10,1.187,0.503,202212,Day,0.424,1670666400,2022
2022/12/10 11:00:00,20221210,0,0,11,1.895,0.804,202212,Day,0.424,1670670000,2022
2022/12/10 12:00:00,20221210,0,0,12,1.245,0.528,202212,Day,0.424,1670673600,2022

## Tariff Files (HDF_example_tariff.*)
The tariff files detail the total period usage and costs/credit for the defined tariffs. If you have specified a FIT rate, that will also appear in this file with the name 'FIT'. These files help most when comparing usage/costs against a bill received for the same period.

JSONL:
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

## Hourly Files (HDF_example_hour.*)
The hourly files show the combined total import and export per common hour across the entire period. There will only be 24 entries in these files. 

JSON:
```json
{"hour": 0, "import": 10.2635, "import_cost": 2.1471, "export": 0, "export_credit": 0}
{"hour": 1, "import": 9.8110, "import_cost": 2.0525, "export": 0, "export_credit": 0}
{"hour": 2, "import": 11.2375, "import_cost": 1.4298, "export": 0, "export_credit": 0}
{"hour": 3, "import": 11.7335, "import_cost": 1.4409, "export": 0, "export_credit": 0}
{"hour": 4, "import": 12.0285, "import_cost": 2.5164, "export": 0, "export_credit": 0}
{"hour": 5, "import": 4.9335, "import_cost": 1.0321, "export": 0, "export_credit": 0}
{"hour": 6, "import": 5.7290, "import_cost": 1.1985, "export": 0, "export_credit": 0}
{"hour": 7, "import": 16.1595, "import_cost": 3.3806, "export": 0, "export_credit": 0}
{"hour": 8, "import": 14.7445, "import_cost": 6.2531, "export": 0, "export_credit": 0}
{"hour": 9, "import": 21.1310, "import_cost": 8.9617, "export": 0, "export_credit": 0}
{"hour": 10, "import": 15.7505, "import_cost": 6.6798, "export": 0, "export_credit": 0}
{"hour": 11, "import": 16.9335, "import_cost": 7.1815, "export": 0, "export_credit": 0}
{"hour": 12, "import": 19.7475, "import_cost": 8.3749, "export": 0, "export_credit": 0}
{"hour": 13, "import": 17.5195, "import_cost": 7.4300, "export": 0, "export_credit": 0}
{"hour": 14, "import": 15.7370, "import_cost": 6.6741, "export": 0, "export_credit": 0}
{"hour": 15, "import": 16.4290, "import_cost": 6.9675, "export": 0, "export_credit": 0}
{"hour": 16, "import": 19.4155, "import_cost": 8.2341, "export": 0, "export_credit": 0}
{"hour": 17, "import": 24.5225, "import_cost": 10.4000, "export": 0, "export_credit": 0}
{"hour": 18, "import": 27.5865, "import_cost": 11.6994, "export": 0, "export_credit": 0}
{"hour": 19, "import": 21.0815, "import_cost": 8.9407, "export": 0, "export_credit": 0}
{"hour": 20, "import": 19.7005, "import_cost": 8.3550, "export": 0, "export_credit": 0}
{"hour": 21, "import": 19.0685, "import_cost": 8.0870, "export": 0, "export_credit": 0}
{"hour": 22, "import": 19.2740, "import_cost": 8.1741, "export": 0, "export_credit": 0}
{"hour": 23, "import": 14.9950, "import_cost": 3.1370, "export": 0, "export_credit": 0}
```
CSV:
```
0,0,0,10.263,2.147
0,0,1,9.811,2.052
0,0,2,11.237,1.43
0,0,3,11.733,1.441
0,0,4,12.029,2.516
0,0,5,4.933,1.032
0,0,6,5.729,1.199
0,0,7,16.16,3.381
0,0,8,14.744,6.253
0,0,9,21.131,8.962
0,0,10,15.75,6.68
0,0,11,16.933,7.181
0,0,12,19.748,8.375
0,0,13,17.519,7.43
0,0,14,15.737,6.674
0,0,15,16.429,6.968
0,0,16,19.415,8.234
0,0,17,24.522,10.4
0,0,18,27.586,11.699
0,0,19,21.082,8.941
0,0,20,19.7,8.355
0,0,21,19.069,8.087
0,0,22,19.274,8.174
0,0,23,14.995,3.137
```

## Daily Files (HDF_example_day.*)
The daily files show the total import and export per full day along with cost/credit details.

JSON:
```json
{"day": "20230301", "import": 9.5665, "import_cost": 3.4319, "export": 0, "export_credit": 0}
{"day": "20230302", "import": 15.0460, "import_cost": 5.4643, "export": 0, "export_credit": 0}
{"day": "20230303", "import": 14.2270, "import_cost": 5.1135, "export": 0, "export_credit": 0}
{"day": "20230304", "import": 19.4025, "import_cost": 7.3516, "export": 0, "export_credit": 0}
{"day": "20230305", "import": 13.2820, "import_cost": 4.7247, "export": 0, "export_credit": 0}
{"day": "20230306", "import": 12.2555, "import_cost": 4.5359, "export": 0, "export_credit": 0}
{"day": "20230307", "import": 12.6015, "import_cost": 4.4604, "export": 0, "export_credit": 0}
{"day": "20230308", "import": 13.6160, "import_cost": 4.9622, "export": 0, "export_credit": 0}
{"day": "20230309", "import": 12.0130, "import_cost": 4.2980, "export": 0, "export_credit": 0}
{"day": "20230310", "import": 18.6770, "import_cost": 6.9732, "export": 0, "export_credit": 0}
{"day": "20230311", "import": 19.0300, "import_cost": 7.1878, "export": 0, "export_credit": 0}
{"day": "20230312", "import": 16.6775, "import_cost": 6.1802, "export": 0, "export_credit": 0}
{"day": "20230313", "import": 11.6480, "import_cost": 4.1066, "export": 0, "export_credit": 0}
{"day": "20230314", "import": 12.8385, "import_cost": 4.4420, "export": 0, "export_credit": 0}
{"day": "20230315", "import": 12.8725, "import_cost": 4.8098, "export": 0, "export_credit": 0}
{"day": "20230316", "import": 14.1310, "import_cost": 5.0686, "export": 0, "export_credit": 0}
{"day": "20230317", "import": 11.5650, "import_cost": 4.0794, "export": 0, "export_credit": 0}
{"day": "20230318", "import": 15.4085, "import_cost": 5.6586, "export": 0, "export_credit": 0}
{"day": "20230319", "import": 15.3670, "import_cost": 5.5451, "export": 0, "export_credit": 0}
{"day": "20230320", "import": 9.2425, "import_cost": 3.4141, "export": 0, "export_credit": 0}
{"day": "20230321", "import": 8.7815, "import_cost": 3.2798, "export": 0, "export_credit": 0}
{"day": "20230322", "import": 13.5900, "import_cost": 4.8975, "export": 0, "export_credit": 0}
{"day": "20230323", "import": 13.3635, "import_cost": 4.8940, "export": 0, "export_credit": 0}
{"day": "20230324", "import": 14.5595, "import_cost": 5.3662, "export": 0, "export_credit": 0}
{"day": "20230325", "import": 19.0635, "import_cost": 7.2975, "export": 0, "export_credit": 0}
{"day": "20230326", "import": 13.0275, "import_cost": 4.8984, "export": 0, "export_credit": 0}
{"day": "20230327", "import": 11.4880, "import_cost": 4.0340, "export": 0, "export_credit": 0}
{"day": "20230328", "import": 12.1915, "import_cost": 4.2725, "export": 0, "export_credit": 0}
```
CSV:
```
20230301,0,0,9.566,3.432
20230302,0,0,15.046,5.464
20230303,0,0,14.227,5.113
20230304,0,0,19.402,7.352
20230305,0,0,13.282,4.725
20230306,0,0,12.255,4.536
20230307,0,0,12.601,4.46
20230308,0,0,13.616,4.962
20230309,0,0,12.013,4.298
20230310,0,0,18.677,6.973
20230311,0,0,19.03,7.188
20230312,0,0,16.677,6.18
20230313,0,0,11.648,4.107
20230314,0,0,12.839,4.442
20230315,0,0,12.872,4.81
20230316,0,0,14.131,5.069
20230317,0,0,11.565,4.079
20230318,0,0,15.409,5.659
20230319,0,0,15.367,5.545
20230320,0,0,9.242,3.414
20230321,0,0,8.781,3.28
20230322,0,0,13.59,4.897
20230323,0,0,13.364,4.894
20230324,0,0,14.559,5.366
20230325,0,0,19.064,7.297
20230326,0,0,13.027,4.898
20230327,0,0,11.488,4.034
20230328,0,0,12.192,4.273
```

## Monthly Files (HDF_example_month.*)
The monthly files show the total import and export per full calendar month along with cost/credit details.

JSON:
```json
{"month": "202303", "import": 385.5325, "import_cost": 140.7476, "export": 0, "export_credit": 0}
```
CSV:
```
export,export_credit,import,import_cost,month
0,0,385.532,140.748,202303
```

## Yearly Files (HDF_example_year.*)
The yearly files show the total import and export per full calendar year along with cost/credit details.

JSON:
```json
{"year": "2023", "import": 385.5325, "import_cost": 140.7476, "export": 0, "export_credit": 0}
```
CSV:
```
export,export_credit,import,import_cost,month
0,0,385.532,140.748,2023
```

