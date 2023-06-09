# ESB HDF Reader

The Electricity Supply Board in Ireland have a data download service available to customers with smart meters. They refer to this data as their harmonised data format. It's essentially power import and export data provided in 30-minute intervals and downloaded in CSV files. It has been an awkward data source in general as the power usage values are timestamped in local time when the usage period ended and also need to be summed up per half-hour and divided by 2 to get real kWh values.

The ```esb_hdf_reader.py``` script can be used to parse this data into a more analytics or spreadsheet-friendly intermediate form. 

## Usage
```
usage: esb_hdf_reader.py [-h] --file FILE --odir ODIR [--timezone TIMEZONE]
                         [--decimal_places DECIMAL_PLACES] [--verbose]

ESB HDF Reader

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           ESB HDF file
  --odir ODIR           Output Directory
  --format {json,csv,both}
                        Output Format
  --timezone TIMEZONE   Timezone
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:4)
  --verbose             Enable verbose output

```

Notes:
* The script is run and pointed at a HDF file as downloaded from the ESB (--file file.csv)
* The output directory is set to control where the script dumps all generated JSONL and CSV files (--odir <dir>)
* The --format option controls output via JSON, CSV or both variants. JSON is output by default
* Timezone can be asserted with the --timezone option. By default, this is set to Europe/Dublin. The ESB HDF data comes in local Europe/Dublin timezone. So this option should not be required.
* Decimal places can be controlled using the --decimal_places option and this defaults to 4. This only affects data written to the CSV files.


## Example Call (using the included example file)
```
python3 energyutils/esb_hdf_reader.py \
            --file energyutils/sample_data/HDF_example.csv \
            --odir Desktop/esb_data

Mon May  1 12:39:51 2023 Parsed 3125 hourly records from /Users/cormac/work/energyutils/sample_data/HDF_example.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-18.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-17.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-16.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-15.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-14.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-13.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-12.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-11.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-10.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-09.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/2023-04-08.jsonl
.........
.........
.........
.........

```

## Sample Files
Each generated file contains hourly data for an entire day. Both JSONL and CSV variants are generated per day. The naming convention is YYYYMMDD.jsonl and YYYYMMDD.csv.

### Example JSONL File
```json
{"ts": 1674950400, "datetime": "2023/01/29 00:00:00", "import": 0.4280, "export": 0.0000, "hour": 0, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674954000, "datetime": "2023/01/29 01:00:00", "import": 0.4085, "export": 0.0000, "hour": 1, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674957600, "datetime": "2023/01/29 02:00:00", "import": 1.5545, "export": 0.0000, "hour": 2, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674961200, "datetime": "2023/01/29 03:00:00", "import": 2.7575, "export": 0.0000, "hour": 3, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674964800, "datetime": "2023/01/29 04:00:00", "import": 2.3275, "export": 0.0000, "hour": 4, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674968400, "datetime": "2023/01/29 05:00:00", "import": 0.0050, "export": 0.0000, "hour": 5, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674972000, "datetime": "2023/01/29 06:00:00", "import": 0.0000, "export": 0.0005, "hour": 6, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674975600, "datetime": "2023/01/29 07:00:00", "import": 0.0015, "export": 0.0010, "hour": 7, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674979200, "datetime": "2023/01/29 08:00:00", "import": 0.0100, "export": 0.0005, "hour": 8, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674982800, "datetime": "2023/01/29 09:00:00", "import": 0.0055, "export": 0.0035, "hour": 9, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674986400, "datetime": "2023/01/29 10:00:00", "import": 0.0025, "export": 0.0015, "hour": 10, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674990000, "datetime": "2023/01/29 11:00:00", "import": 0.0055, "export": 0.0060, "hour": 11, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674993600, "datetime": "2023/01/29 12:00:00", "import": 0.0855, "export": 0.0345, "hour": 12, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1674997200, "datetime": "2023/01/29 13:00:00", "import": 0.0360, "export": 0.0290, "hour": 13, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675000800, "datetime": "2023/01/29 14:00:00", "import": 0.0140, "export": 0.0100, "hour": 14, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675004400, "datetime": "2023/01/29 15:00:00", "import": 0.0235, "export": 0.0080, "hour": 15, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675008000, "datetime": "2023/01/29 16:00:00", "import": 0.0280, "export": 0.0175, "hour": 16, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675011600, "datetime": "2023/01/29 17:00:00", "import": 0.0380, "export": 0.0045, "hour": 17, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675015200, "datetime": "2023/01/29 18:00:00", "import": 0.3910, "export": 0.0505, "hour": 18, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675018800, "datetime": "2023/01/29 19:00:00", "import": 0.7515, "export": 0.0000, "hour": 19, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675022400, "datetime": "2023/01/29 20:00:00", "import": 0.6370, "export": 0.0000, "hour": 20, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675026000, "datetime": "2023/01/29 21:00:00", "import": 0.5590, "export": 0.0000, "hour": 21, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675029600, "datetime": "2023/01/29 22:00:00", "import": 0.5300, "export": 0.0000, "hour": 22, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
{"ts": 1675033200, "datetime": "2023/01/29 23:00:00", "import": 0.4575, "export": 0.0000, "hour": 23, "day": "2023-01-29", "month": "2023-01", "year": "2023", "weekday": "7 Sun", "week": "2023-04"}
```

### Example CSV File (only generated with --format csv)
```csv
datetime,day,export,hour,import,month,ts,week,weekday,year
2023/01/29 00:00:00,2023-01-29,0.0,0,0.428,2023-01,1674950400,2023-04,7 Sun,2023
2023/01/29 01:00:00,2023-01-29,0.0,1,0.4085,2023-01,1674954000,2023-04,7 Sun,2023
2023/01/29 02:00:00,2023-01-29,0.0,2,1.5545,2023-01,1674957600,2023-04,7 Sun,2023
2023/01/29 03:00:00,2023-01-29,0.0,3,2.7575,2023-01,1674961200,2023-04,7 Sun,2023
2023/01/29 04:00:00,2023-01-29,0.0,4,2.3275,2023-01,1674964800,2023-04,7 Sun,2023
2023/01/29 05:00:00,2023-01-29,0.0,5,0.005,2023-01,1674968400,2023-04,7 Sun,2023
2023/01/29 06:00:00,2023-01-29,0.0005,6,0.0,2023-01,1674972000,2023-04,7 Sun,2023
2023/01/29 07:00:00,2023-01-29,0.001,7,0.0015,2023-01,1674975600,2023-04,7 Sun,2023
2023/01/29 08:00:00,2023-01-29,0.0005,8,0.01,2023-01,1674979200,2023-04,7 Sun,2023
2023/01/29 09:00:00,2023-01-29,0.0035,9,0.0055,2023-01,1674982800,2023-04,7 Sun,2023
2023/01/29 10:00:00,2023-01-29,0.0015,10,0.0025,2023-01,1674986400,2023-04,7 Sun,2023
2023/01/29 11:00:00,2023-01-29,0.006,11,0.0055,2023-01,1674990000,2023-04,7 Sun,2023
2023/01/29 12:00:00,2023-01-29,0.0345,12,0.0855,2023-01,1674993600,2023-04,7 Sun,2023
2023/01/29 13:00:00,2023-01-29,0.029,13,0.036,2023-01,1674997200,2023-04,7 Sun,2023
2023/01/29 14:00:00,2023-01-29,0.01,14,0.014,2023-01,1675000800,2023-04,7 Sun,2023
2023/01/29 15:00:00,2023-01-29,0.008,15,0.0235,2023-01,1675004400,2023-04,7 Sun,2023
2023/01/29 16:00:00,2023-01-29,0.0175,16,0.028,2023-01,1675008000,2023-04,7 Sun,2023
2023/01/29 17:00:00,2023-01-29,0.0045,17,0.038,2023-01,1675011600,2023-04,7 Sun,2023
2023/01/29 18:00:00,2023-01-29,0.0505,18,0.391,2023-01,1675015200,2023-04,7 Sun,2023
2023/01/29 19:00:00,2023-01-29,0.0,19,0.7515,2023-01,1675018800,2023-04,7 Sun,2023
2023/01/29 20:00:00,2023-01-29,0.0,20,0.637,2023-01,1675022400,2023-04,7 Sun,2023
2023/01/29 21:00:00,2023-01-29,0.0,21,0.559,2023-01,1675026000,2023-04,7 Sun,2023
2023/01/29 22:00:00,2023-01-29,0.0,22,0.53,2023-01,1675029600,2023-04,7 Sun,2023
2023/01/29 23:00:00,2023-01-29,0.0,23,0.4575,2023-01,1675033200,2023-04,7 Sun,2023
```
