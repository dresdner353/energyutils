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
  --timezone TIMEZONE   Timezone
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:4)
  --verbose             Enable verbose output

```

Notes:
* The script is run and pointed at a HDF file as downloaded from the ESB (--file file.csv)
* The output directory is set to control where the script dumps all generated JSONL and CSV files (--odir <dir>)
* Timezone can be asserted with the --timezone option. By default, this is set to Europe/Dublin. The ESB HDF data comes in local Europe/Dublin timezone. So this option should not be required.
* Decimal places can be controlled using the --decimal_places option and this defaults to 4. This only affects data written to the CSV files.


## Example Call (using the included example file)
```
python3 energyutils/esb_hdf_reader.py \
            --file energyutils/HDF_example.csv \
            --odir Desktop/esb_data

Mon May  1 12:39:51 2023 Parsed 3125 hourly records from /Users/cormac/work/energyutils/HDF_example.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230418.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230418.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230417.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230417.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230416.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230416.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230415.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230415.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230414.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230414.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230413.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230413.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230412.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230412.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230411.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230411.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230410.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230410.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230409.jsonl
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230409.csv
Mon May  1 12:39:51 2023 Writing to Desktop/esb_data/20230408.jsonl
.........
.........
.........
.........

```

## Sample Files
Each generated file contains hourly data for an entire day. Both JSONL and CSV variants are generated per day. The naming convention is YYYYMMDD.jsonl and YYYYMMDD.csv.

### Example JSONL File
```json
{"ts": 1670976000, "datetime": "2022/12/14 00:00:00", "import": 0.4165, "export": 0, "hour": 0, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670979600, "datetime": "2022/12/14 01:00:00", "import": 0.8580, "export": 0, "hour": 1, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670983200, "datetime": "2022/12/14 02:00:00", "import": 0.2370, "export": 0, "hour": 2, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670986800, "datetime": "2022/12/14 03:00:00", "import": 0.2095, "export": 0, "hour": 3, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670990400, "datetime": "2022/12/14 04:00:00", "import": 0.2240, "export": 0, "hour": 4, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670994000, "datetime": "2022/12/14 05:00:00", "import": 0.1995, "export": 0, "hour": 5, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1670997600, "datetime": "2022/12/14 06:00:00", "import": 0.2650, "export": 0, "hour": 6, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671001200, "datetime": "2022/12/14 07:00:00", "import": 0.8110, "export": 0, "hour": 7, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671004800, "datetime": "2022/12/14 08:00:00", "import": 0.5395, "export": 0, "hour": 8, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671008400, "datetime": "2022/12/14 09:00:00", "import": 0.2635, "export": 0, "hour": 9, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671012000, "datetime": "2022/12/14 10:00:00", "import": 0.4330, "export": 0, "hour": 10, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671015600, "datetime": "2022/12/14 11:00:00", "import": 0.2900, "export": 0, "hour": 11, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671019200, "datetime": "2022/12/14 12:00:00", "import": 0.3025, "export": 0, "hour": 12, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671022800, "datetime": "2022/12/14 13:00:00", "import": 0.4230, "export": 0, "hour": 13, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671026400, "datetime": "2022/12/14 14:00:00", "import": 0.2540, "export": 0, "hour": 14, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671030000, "datetime": "2022/12/14 15:00:00", "import": 0.5070, "export": 0, "hour": 15, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671033600, "datetime": "2022/12/14 16:00:00", "import": 0.5155, "export": 0, "hour": 16, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671037200, "datetime": "2022/12/14 17:00:00", "import": 1.0015, "export": 0, "hour": 17, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671040800, "datetime": "2022/12/14 18:00:00", "import": 0.8060, "export": 0, "hour": 18, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671044400, "datetime": "2022/12/14 19:00:00", "import": 0.7120, "export": 0, "hour": 19, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671048000, "datetime": "2022/12/14 20:00:00", "import": 0.7120, "export": 0, "hour": 20, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671051600, "datetime": "2022/12/14 21:00:00", "import": 0.6480, "export": 0, "hour": 21, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671055200, "datetime": "2022/12/14 22:00:00", "import": 1.0370, "export": 0, "hour": 22, "day": "20221214", "month": "202212", "year": "2022"}
{"ts": 1671058800, "datetime": "2022/12/14 23:00:00", "import": 0.5620, "export": 0, "hour": 23, "day": "20221214", "month": "202212", "year": "2022"}
```

### Example CSV File
```csv
datetime,day,export,hour,import,month,ts,year
2022/12/14 00:00:00,20221214,0,0,0.416,202212,1670976000,2022
2022/12/14 01:00:00,20221214,0,1,0.858,202212,1670979600,2022
2022/12/14 02:00:00,20221214,0,2,0.237,202212,1670983200,2022
2022/12/14 03:00:00,20221214,0,3,0.21,202212,1670986800,2022
2022/12/14 04:00:00,20221214,0,4,0.224,202212,1670990400,2022
2022/12/14 05:00:00,20221214,0,5,0.2,202212,1670994000,2022
2022/12/14 06:00:00,20221214,0,6,0.265,202212,1670997600,2022
2022/12/14 07:00:00,20221214,0,7,0.811,202212,1671001200,2022
2022/12/14 08:00:00,20221214,0,8,0.539,202212,1671004800,2022
2022/12/14 09:00:00,20221214,0,9,0.264,202212,1671008400,2022
2022/12/14 10:00:00,20221214,0,10,0.433,202212,1671012000,2022
2022/12/14 11:00:00,20221214,0,11,0.29,202212,1671015600,2022
2022/12/14 12:00:00,20221214,0,12,0.302,202212,1671019200,2022
2022/12/14 13:00:00,20221214,0,13,0.423,202212,1671022800,2022
2022/12/14 14:00:00,20221214,0,14,0.254,202212,1671026400,2022
2022/12/14 15:00:00,20221214,0,15,0.507,202212,1671030000,2022
2022/12/14 16:00:00,20221214,0,16,0.516,202212,1671033600,2022
2022/12/14 17:00:00,20221214,0,17,1.002,202212,1671037200,2022
2022/12/14 18:00:00,20221214,0,18,0.806,202212,1671040800,2022
2022/12/14 19:00:00,20221214,0,19,0.712,202212,1671044400,2022
2022/12/14 20:00:00,20221214,0,20,0.712,202212,1671048000,2022
2022/12/14 21:00:00,20221214,0,21,0.648,202212,1671051600,2022
2022/12/14 22:00:00,20221214,0,22,1.037,202212,1671055200,2022
2022/12/14 23:00:00,20221214,0,23,0.562,202212,1671058800,2022
```

### Field Descriptions
* ts   
The EPOCH timestamp of the start of the consumption hour
* datetime   
A string datetime in YYYY/MM/DD HH:MM:SS in local time. 
* hour
Hour of given day 0-23
* day
Day in YYYYMMDD format
* month
Month in YYYYMM format
* year
Year in YYYY format
* import   
Import kWh units
* export   
Export kWh units
