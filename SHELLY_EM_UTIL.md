# Shelly EM Data Utility

The Shelly EM is a small ESP8266-based device that can be used to monitor 1-2 AC power sources and measure power consumption and export. The device is small enough to be fitted inside a typical RCB distribution unit. The power monitoring is achieved via CT clamps. 

The device operates as a client on a WiFi network and may either be accessed directly or via the Shelly Cloud APIs. 

The ```shelly_em_data_util.py``` script is designed to retrieve Shelly EM data from the Shelly Cloud service. For this to be possible, you need to:
* Enable your Shelly EM for cloud (so it can upload usage data to the cloud)
* Obtain a cloud API auth key from your Shelly account.
* Obtain your Shelly EM device ID
* Get the recommended Shelly Cloud hostname from your account
* The expected CT clamp wiring is:
   - P1 -> Grid Import, clamp direction for incoming current from the grid
   - P2 -> Solar Generation, clamp direction for incoming current from the solar inverter

## Usage
```
usage: shelly_em_data_util.py [-h] --host HOST [--odir ODIR] [--days DAYS] --id ID --auth_key AUTH_KEY
                              [--incl_today] [--decimal_places DECIMAL_PLACES] [--verbose]

Shelly EM Data Retrieval Utility

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Shelly API Host
  --odir ODIR           Output Directory for generated files
  --days DAYS           Backfill in days (def 30)
  --id ID               Device ID
  --auth_key AUTH_KEY   API Auth Key
  --incl_today          Request data for current incomplete day
  --decimal_places DECIMAL_PLACES
                        Decimal Places (def:3)
  --verbose             Enable verbose output
```
Notes:
* The API host is set by the --host arg. 
* The --id option sets the device ID to query
* The output directory is set by --odir but this also defaults to ~/.shellyemdata
* The --days option sets the number of full days to retrieve since yesterday
   - Data for any given day is only retrieved when the target YYYYMMDD_hour.jsonl file is not present in the output directory
   - So retrieval acts incrementally, only pulling data for days you do not already have. 
* The --auth_key is the API key you retrieved from your account
* The --incl_today option can be added to additionally request data for the current incomplete day. Normally the latest daya retrieved is yesterday

## Example Run
```
% python3  work/energyutils/shelly_em_data_util.py \
        --host shelly-XX-eu.shelly.cloud \
        --id XXXXXXXXXXXX \
        --auth_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
        --days 10

Mon May  1 12:29:30 2023 Getting data for 2023-04-30 00:00:00s
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230430.jsonl
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230430.csv
Mon May  1 12:29:31 2023 Getting data for 2023-04-29 00:00:00s
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230429.jsonl
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230429.csv
Mon May  1 12:29:31 2023 Getting data for 2023-04-28 00:00:00s
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230428.jsonl
Mon May  1 12:29:31 2023 Writing to /Users/cormac/.shellyemdata/20230428.csv
Mon May  1 12:29:31 2023 Getting data for 2023-04-27 00:00:00s
Mon May  1 12:29:32 2023 Writing to /Users/cormac/.shellyemdata/20230427.jsonl
Mon May  1 12:29:32 2023 Writing to /Users/cormac/.shellyemdata/20230427.csv
Mon May  1 12:29:32 2023 Getting data for 2023-04-26 00:00:00s
Mon May  1 12:29:32 2023 Writing to /Users/cormac/.shellyemdata/20230426.jsonl
Mon May  1 12:29:32 2023 Writing to /Users/cormac/.shellyemdata/20230426.csv
Mon May  1 12:29:32 2023 Getting data for 2023-04-25 00:00:00s
Mon May  1 12:29:33 2023 Writing to /Users/cormac/.shellyemdata/20230425.jsonl
Mon May  1 12:29:33 2023 Writing to /Users/cormac/.shellyemdata/20230425.csv
Mon May  1 12:29:33 2023 Getting data for 2023-04-24 00:00:00s
Mon May  1 12:29:33 2023 Writing to /Users/cormac/.shellyemdata/20230424.jsonl
Mon May  1 12:29:33 2023 Writing to /Users/cormac/.shellyemdata/20230424.csv
Mon May  1 12:29:33 2023 Getting data for 2023-04-23 00:00:00s
Mon May  1 12:29:34 2023 Writing to /Users/cormac/.shellyemdata/20230423.jsonl
Mon May  1 12:29:34 2023 Writing to /Users/cormac/.shellyemdata/20230423.csv
Mon May  1 12:29:34 2023 Getting data for 2023-04-22 00:00:00s
Mon May  1 12:29:34 2023 Writing to /Users/cormac/.shellyemdata/20230422.jsonl
Mon May  1 12:29:34 2023 Writing to /Users/cormac/.shellyemdata/20230422.csv
Mon May  1 12:29:34 2023 Getting data for 2023-04-21 00:00:00s
Mon May  1 12:29:35 2023 Writing to /Users/cormac/.shellyemdata/20230421.jsonl
Mon May  1 12:29:35 2023 Writing to /Users/cormac/.shellyemdata/20230421.csv
```

## Sample Files
Each generated file contains hourly data for an entire day. Both JSONL and CSV variants are generated per day. The naming convention is YYYYMMDD.jsonl and YYYYMMDD.csv.

### Example JSONL File
```json
{"ts": 1682204400, "datetime": "2023/04/23 00:00:00", "import": 0.2204, "export": 0.0000, "hour": 0, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2204}
{"ts": 1682208000, "datetime": "2023/04/23 01:00:00", "import": 0.5702, "export": 0.0000, "hour": 1, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5702}
{"ts": 1682211600, "datetime": "2023/04/23 02:00:00", "import": 0.2022, "export": 0.0000, "hour": 2, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2022}
{"ts": 1682215200, "datetime": "2023/04/23 03:00:00", "import": 0.7248, "export": 0.0000, "hour": 3, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.7248}
{"ts": 1682218800, "datetime": "2023/04/23 04:00:00", "import": 0.2424, "export": 0.0000, "hour": 4, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2424}
{"ts": 1682222400, "datetime": "2023/04/23 05:00:00", "import": 0.1822, "export": 0.0000, "hour": 5, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.1822}
{"ts": 1682226000, "datetime": "2023/04/23 06:00:00", "import": 0.1910, "export": 0.0000, "hour": 6, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.1910}
{"ts": 1682229600, "datetime": "2023/04/23 07:00:00", "import": 0.1883, "export": 0.0000, "hour": 7, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.1883}
{"ts": 1682233200, "datetime": "2023/04/23 08:00:00", "import": 0.2155, "export": 0.0000, "hour": 8, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2155}
{"ts": 1682236800, "datetime": "2023/04/23 09:00:00", "import": 0.4580, "export": 0.0000, "hour": 9, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.4580}
{"ts": 1682240400, "datetime": "2023/04/23 10:00:00", "import": 0.2347, "export": 0.0000, "hour": 10, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2347}
{"ts": 1682244000, "datetime": "2023/04/23 11:00:00", "import": 0.2378, "export": 0.0000, "hour": 11, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.2378}
{"ts": 1682247600, "datetime": "2023/04/23 12:00:00", "import": 0.3397, "export": 0.0000, "hour": 12, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.3397}
{"ts": 1682251200, "datetime": "2023/04/23 13:00:00", "import": 0.5761, "export": 0.0000, "hour": 13, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5761}
{"ts": 1682254800, "datetime": "2023/04/23 14:00:00", "import": 0.6475, "export": 0.0000, "hour": 14, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.6475}
{"ts": 1682258400, "datetime": "2023/04/23 15:00:00", "import": 0.5648, "export": 0.0000, "hour": 15, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5648}
{"ts": 1682262000, "datetime": "2023/04/23 16:00:00", "import": 0.5572, "export": 0.0000, "hour": 16, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5572}
{"ts": 1682265600, "datetime": "2023/04/23 17:00:00", "import": 0.5142, "export": 0.0000, "hour": 17, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5142}
{"ts": 1682269200, "datetime": "2023/04/23 18:00:00", "import": 0.4518, "export": 0.0000, "hour": 18, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.4518}
{"ts": 1682272800, "datetime": "2023/04/23 19:00:00", "import": 0.4121, "export": 0.0000, "hour": 19, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.4121}
{"ts": 1682276400, "datetime": "2023/04/23 20:00:00", "import": 0.7231, "export": 0.0000, "hour": 20, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.7231}
{"ts": 1682280000, "datetime": "2023/04/23 21:00:00", "import": 0.5967, "export": 0.0000, "hour": 21, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5967}
{"ts": 1682283600, "datetime": "2023/04/23 22:00:00", "import": 0.5816, "export": 0.0000, "hour": 22, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.5816}
{"ts": 1682287200, "datetime": "2023/04/23 23:00:00", "import": 0.4998, "export": 0.0000, "hour": 23, "day": "20230423", "month": "202304", "year": "2023", "solar": 0.0000, "consumed": 0.4998}
```

### Example CSV File
```csv
consumed,datetime,day,export,hour,import,month,solar,ts,year
0.22,2023/04/23 00:00:00,20230423,0.0,0,0.22,202304,0.0,1682204400,2023
0.57,2023/04/23 01:00:00,20230423,0.0,1,0.57,202304,0.0,1682208000,2023
0.202,2023/04/23 02:00:00,20230423,0.0,2,0.202,202304,0.0,1682211600,2023
0.725,2023/04/23 03:00:00,20230423,0.0,3,0.725,202304,0.0,1682215200,2023
0.242,2023/04/23 04:00:00,20230423,0.0,4,0.242,202304,0.0,1682218800,2023
0.182,2023/04/23 05:00:00,20230423,0.0,5,0.182,202304,0.0,1682222400,2023
0.191,2023/04/23 06:00:00,20230423,0.0,6,0.191,202304,0.0,1682226000,2023
0.188,2023/04/23 07:00:00,20230423,0.0,7,0.188,202304,0.0,1682229600,2023
0.215,2023/04/23 08:00:00,20230423,0.0,8,0.215,202304,0.0,1682233200,2023
0.458,2023/04/23 09:00:00,20230423,0.0,9,0.458,202304,0.0,1682236800,2023
0.235,2023/04/23 10:00:00,20230423,0.0,10,0.235,202304,0.0,1682240400,2023
0.238,2023/04/23 11:00:00,20230423,0.0,11,0.238,202304,0.0,1682244000,2023
0.34,2023/04/23 12:00:00,20230423,0.0,12,0.34,202304,0.0,1682247600,2023
0.576,2023/04/23 13:00:00,20230423,0.0,13,0.576,202304,0.0,1682251200,2023
0.648,2023/04/23 14:00:00,20230423,0.0,14,0.648,202304,0.0,1682254800,2023
0.565,2023/04/23 15:00:00,20230423,0.0,15,0.565,202304,0.0,1682258400,2023
0.557,2023/04/23 16:00:00,20230423,0.0,16,0.557,202304,0.0,1682262000,2023
0.514,2023/04/23 17:00:00,20230423,0.0,17,0.514,202304,0.0,1682265600,2023
0.452,2023/04/23 18:00:00,20230423,0.0,18,0.452,202304,0.0,1682269200,2023
0.412,2023/04/23 19:00:00,20230423,0.0,19,0.412,202304,0.0,1682272800,2023
0.723,2023/04/23 20:00:00,20230423,0.0,20,0.723,202304,0.0,1682276400,2023
0.597,2023/04/23 21:00:00,20230423,0.0,21,0.597,202304,0.0,1682280000,2023
0.582,2023/04/23 22:00:00,20230423,0.0,22,0.582,202304,0.0,1682283600,2023
0.5,2023/04/23 23:00:00,20230423,0.0,23,0.5,202304,0.0,1682287200,2023
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
* solar   
Solar kWh units
* consumed   
Consumed kWh units
