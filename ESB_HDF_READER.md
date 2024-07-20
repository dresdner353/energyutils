# ESB HDF Reader

The Electricity Supply Board in Ireland have a data download service available to customers with smart meters. They refer to this data as their harmonised data format. It's essentially power import and export data provided in 30-minute intervals and downloaded in CSV files. It has been an awkward data source in general as the power usage values are timestamped in local time when the usage period ends and also need to be summed up per half-hour and divided by 2 to get real kWh values.

Note: In July 2024, ESBN released updates to the download formats and now HDF files may be downloaded in the bot 30-min kW and 30-min kWh calculations. Either variant will work with this script as it detects the variant automatically. 

The ```esb_hdf_reader.py``` script can be used to parse this data into a more analytics or spreadsheet-friendly intermediate form. 

## Usage
```
usage: esb_hdf_reader.py [-h] --file FILE --odir ODIR [--timezone TIMEZONE]
                         [--verbose]

ESB HDF Reader

optional arguments:
  -h, --help           show this help message and exit
  --file FILE [FILE ...]
                       ESB HDF file list or directory
  --odir ODIR          Output Directory
  --timezone TIMEZONE  Timezone
  --partial_days       Include incomplete partial days (skipped by default)
  --verbose            Enable verbose output
```

Options:
* --file FILE [FILE ...]  
This specifies the ESB HDF file to use as input. You can also specifiy multiple files here or use a wildcard like HDF*.csv as a way of passing in the pattern of files to process. Another approach is to specifiy a directory and the script will load all .csv files it finds in that directory. The data from each separate file is combined accordingly and any duplicates will automatically overwrite each other. 
* --odir /path/to/output/directory  
This specifies the output directory for the processed data. Each day is written to a separate JSONL file, with each hour being a line in that file
* --timezone TIMEZONE  
Allows for specifying of a timezone. The default is Europe/Dublin and should be fine for any processing within Ireland the UK. 
* --partial_days  
This optional flag instructs the script to include incomplete days where the full 24 hours of data is not present. If this option is omitted, so will any incomplete days from the generated files. Usually with ESB HDF files, they both begin and terminate with incomplete days, so it is recommended you omit this flag unless a larger number of incomplete days are present and you still want a best effort calculation.

## Example Call (using the included example file)
```
python3 energyutils/esb_hdf_reader.py \
            --file energyutils/sample_data/HDF_example.csv \
            --odir Desktop/esb_data

Mon May  1 12:39:51 2023 Parsed 3125 hourly records from /Users/cormac/work/energyutils/sample_data/HDF_example.csv
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-18.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-17.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-16.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-15.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-14.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-13.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-12.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-11.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-10.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-09.jsonl
Mon May  1 12:39:51 2023 Writing Desktop/esb_data/2023-04-08.jsonl
.........
.........
.........
.........

```

## Sample File
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
