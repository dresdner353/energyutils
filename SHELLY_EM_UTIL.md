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
* The API host is set by the --host arg. This mandatoy
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
        --host shelly-63-eu.shelly.cloud \
        --id XXXXXXXXXXXX \
        --auth_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
        --days 10

Sun Apr 23 19:20:11 2023 Getting data for 2023-04-22 00:00:00s
Sun Apr 23 19:20:12 2023 Writing hour data to /Users/cormac/.shellyemdata/20230422_hour.jsonl
Sun Apr 23 19:20:12 2023 Writing hour data to /Users/cormac/.shellyemdata/20230422_hour.csv
Sun Apr 23 19:20:12 2023 Getting data for 2023-04-21 00:00:00s
Sun Apr 23 19:20:12 2023 Writing hour data to /Users/cormac/.shellyemdata/20230421_hour.jsonl
Sun Apr 23 19:20:12 2023 Writing hour data to /Users/cormac/.shellyemdata/20230421_hour.csv
Sun Apr 23 19:20:12 2023 Getting data for 2023-04-20 00:00:00s
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230420_hour.jsonl
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230420_hour.csv
Sun Apr 23 19:20:13 2023 Getting data for 2023-04-19 00:00:00s
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230419_hour.jsonl
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230419_hour.csv
Sun Apr 23 19:20:13 2023 Getting data for 2023-04-18 00:00:00s
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230418_hour.jsonl
Sun Apr 23 19:20:13 2023 Writing hour data to /Users/cormac/.shellyemdata/20230418_hour.csv
Sun Apr 23 19:20:13 2023 Getting data for 2023-04-17 00:00:00s
Sun Apr 23 19:20:14 2023 Writing hour data to /Users/cormac/.shellyemdata/20230417_hour.jsonl
Sun Apr 23 19:20:14 2023 Writing hour data to /Users/cormac/.shellyemdata/20230417_hour.csv
Sun Apr 23 19:20:14 2023 Getting data for 2023-04-16 00:00:00s
Sun Apr 23 19:20:14 2023 Writing hour data to /Users/cormac/.shellyemdata/20230416_hour.jsonl
Sun Apr 23 19:20:14 2023 Writing hour data to /Users/cormac/.shellyemdata/20230416_hour.csv
Sun Apr 23 19:20:14 2023 Getting data for 2023-04-15 00:00:00s
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230415_hour.jsonl
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230415_hour.csv
Sun Apr 23 19:20:15 2023 Getting data for 2023-04-14 00:00:00s
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230414_hour.jsonl
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230414_hour.csv
Sun Apr 23 19:20:15 2023 Getting data for 2023-04-13 00:00:00s
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230413_hour.jsonl
Sun Apr 23 19:20:15 2023 Writing hour data to /Users/cormac/.shellyemdata/20230413_hour.csv
```

## Sample Files
Each generated files is named YYYYMMDD_hour.jsonl and YYYYMMDD_hour.csv

### Example JSONL File
```json
{"ts": 1680044400, "datetime": "2023/03/29 00:00:00", "import": 0.40762, "export": 0.0, "hour": 0, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.40762}
{"ts": 1680048000, "datetime": "2023/03/29 01:00:00", "import": 0.2341, "export": 0.0, "hour": 1, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.2341}
{"ts": 1680051600, "datetime": "2023/03/29 02:00:00", "import": 0.41236, "export": 0.0, "hour": 2, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.41236}
{"ts": 1680055200, "datetime": "2023/03/29 03:00:00", "import": 0.30924, "export": 0.0, "hour": 3, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.30924}
{"ts": 1680058800, "datetime": "2023/03/29 04:00:00", "import": 0.65054, "export": 0.0, "hour": 4, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.65054}
{"ts": 1680062400, "datetime": "2023/03/29 05:00:00", "import": 0.16457, "export": 0.0, "hour": 5, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.16457}
{"ts": 1680066000, "datetime": "2023/03/29 06:00:00", "import": 0.17308, "export": 0.0, "hour": 6, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.17308}
{"ts": 1680069600, "datetime": "2023/03/29 07:00:00", "import": 0.58873, "export": 0.0, "hour": 7, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.58873}
{"ts": 1680073200, "datetime": "2023/03/29 08:00:00", "import": 0.26086000000000004, "export": 0.0, "hour": 8, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.26086000000000004}
{"ts": 1680076800, "datetime": "2023/03/29 09:00:00", "import": 0.20024, "export": 0.0, "hour": 9, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.20024}
{"ts": 1680080400, "datetime": "2023/03/29 10:00:00", "import": 0.21928, "export": 0.0, "hour": 10, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.21928}
{"ts": 1680084000, "datetime": "2023/03/29 11:00:00", "import": 0.23954, "export": 0.0, "hour": 11, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.23954}
{"ts": 1680087600, "datetime": "2023/03/29 12:00:00", "import": 0.6045499999999999, "export": 0.0, "hour": 12, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.6045499999999999}
{"ts": 1680091200, "datetime": "2023/03/29 13:00:00", "import": 0.20205, "export": 0.0, "hour": 13, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.20205}
{"ts": 1680094800, "datetime": "2023/03/29 14:00:00", "import": 0.28997, "export": 0.0, "hour": 14, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.28997}
{"ts": 1680098400, "datetime": "2023/03/29 15:00:00", "import": 0.68952, "export": 0.0, "hour": 15, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.68952}
{"ts": 1680102000, "datetime": "2023/03/29 16:00:00", "import": 0.33292, "export": 0.0, "hour": 16, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.33292}
{"ts": 1680105600, "datetime": "2023/03/29 17:00:00", "import": 0.70727, "export": 0.0, "hour": 17, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.70727}
{"ts": 1680109200, "datetime": "2023/03/29 18:00:00", "import": 0.47598, "export": 0.0, "hour": 18, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.47598}
{"ts": 1680112800, "datetime": "2023/03/29 19:00:00", "import": 0.46469, "export": 0.0, "hour": 19, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.46469}
{"ts": 1680116400, "datetime": "2023/03/29 20:00:00", "import": 0.5719, "export": 0.0, "hour": 20, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.5719}
{"ts": 1680120000, "datetime": "2023/03/29 21:00:00", "import": 0.82553, "export": 0.0, "hour": 21, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.82553}
{"ts": 1680123600, "datetime": "2023/03/29 22:00:00", "import": 0.68426, "export": 0.0, "hour": 22, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.68426}
{"ts": 1680127200, "datetime": "2023/03/29 23:00:00", "import": 0.41863, "export": 0.0, "hour": 23, "day": "20230329", "month": "202303", "year": "2023", "solar": 0.0, "consumed": 0.41863}
```

### Example CSV File
```csv
consumed,datetime,day,export,hour,import,month,solar,ts,year
0.408,2023/03/29 00:00:00,20230329,0.0,0,0.408,202303,0.0,1680044400,2023
0.234,2023/03/29 01:00:00,20230329,0.0,1,0.234,202303,0.0,1680048000,2023
0.412,2023/03/29 02:00:00,20230329,0.0,2,0.412,202303,0.0,1680051600,2023
0.309,2023/03/29 03:00:00,20230329,0.0,3,0.309,202303,0.0,1680055200,2023
0.651,2023/03/29 04:00:00,20230329,0.0,4,0.651,202303,0.0,1680058800,2023
0.165,2023/03/29 05:00:00,20230329,0.0,5,0.165,202303,0.0,1680062400,2023
0.173,2023/03/29 06:00:00,20230329,0.0,6,0.173,202303,0.0,1680066000,2023
0.589,2023/03/29 07:00:00,20230329,0.0,7,0.589,202303,0.0,1680069600,2023
0.261,2023/03/29 08:00:00,20230329,0.0,8,0.261,202303,0.0,1680073200,2023
0.2,2023/03/29 09:00:00,20230329,0.0,9,0.2,202303,0.0,1680076800,2023
0.219,2023/03/29 10:00:00,20230329,0.0,10,0.219,202303,0.0,1680080400,2023
0.24,2023/03/29 11:00:00,20230329,0.0,11,0.24,202303,0.0,1680084000,2023
0.605,2023/03/29 12:00:00,20230329,0.0,12,0.605,202303,0.0,1680087600,2023
0.202,2023/03/29 13:00:00,20230329,0.0,13,0.202,202303,0.0,1680091200,2023
0.29,2023/03/29 14:00:00,20230329,0.0,14,0.29,202303,0.0,1680094800,2023
0.69,2023/03/29 15:00:00,20230329,0.0,15,0.69,202303,0.0,1680098400,2023
0.333,2023/03/29 16:00:00,20230329,0.0,16,0.333,202303,0.0,1680102000,2023
0.707,2023/03/29 17:00:00,20230329,0.0,17,0.707,202303,0.0,1680105600,2023
0.476,2023/03/29 18:00:00,20230329,0.0,18,0.476,202303,0.0,1680109200,2023
0.465,2023/03/29 19:00:00,20230329,0.0,19,0.465,202303,0.0,1680112800,2023
0.572,2023/03/29 20:00:00,20230329,0.0,20,0.572,202303,0.0,1680116400,2023
0.826,2023/03/29 21:00:00,20230329,0.0,21,0.826,202303,0.0,1680120000,2023
0.684,2023/03/29 22:00:00,20230329,0.0,22,0.684,202303,0.0,1680123600,2023
0.419,2023/03/29 23:00:00,20230329,0.0,23,0.419,202303,0.0,1680127200,2023
```
### Field Descriptions
* ts   
The EPOCH timestamp of the start of the consumption hour
* datetime   
A string datetime in YYYY/MM/DD HH:MM:SS in local time. The timezone for your device is retrieved in the Shelly API call
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
