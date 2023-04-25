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
{"ts": 1681426800, "datetime": "2023/04/14 00:00:00", "import": 0.64726, "export": 0.0, "solar": 0.0, "consumed": 0.64726}
{"ts": 1681430400, "datetime": "2023/04/14 01:00:00", "import": 0.22699, "export": 0.0, "solar": 0.0, "consumed": 0.22699}
{"ts": 1681434000, "datetime": "2023/04/14 02:00:00", "import": 0.78375, "export": 0.0, "solar": 0.0, "consumed": 0.78375}
{"ts": 1681437600, "datetime": "2023/04/14 03:00:00", "import": 0.18597999999999998, "export": 0.0, "solar": 0.0, "consumed": 0.18597999999999998}
{"ts": 1681441200, "datetime": "2023/04/14 04:00:00", "import": 0.16427, "export": 0.0, "solar": 0.0, "consumed": 0.16427}
{"ts": 1681444800, "datetime": "2023/04/14 05:00:00", "import": 0.18115, "export": 0.0, "solar": 0.0, "consumed": 0.18115}
{"ts": 1681448400, "datetime": "2023/04/14 06:00:00", "import": 0.20567, "export": 0.0, "solar": 0.0, "consumed": 0.20567}
{"ts": 1681452000, "datetime": "2023/04/14 07:00:00", "import": 0.19488999999999998, "export": 0.0, "solar": 0.0, "consumed": 0.19488999999999998}
{"ts": 1681455600, "datetime": "2023/04/14 08:00:00", "import": 0.19995, "export": 0.0, "solar": 0.0, "consumed": 0.19995}
{"ts": 1681459200, "datetime": "2023/04/14 09:00:00", "import": 0.2094, "export": 0.0, "solar": 0.0, "consumed": 0.2094}
{"ts": 1681462800, "datetime": "2023/04/14 10:00:00", "import": 0.18947999999999998, "export": 0.0, "solar": 0.0, "consumed": 0.18947999999999998}
{"ts": 1681466400, "datetime": "2023/04/14 11:00:00", "import": 0.34991, "export": 0.0, "solar": 0.0, "consumed": 0.34991}
{"ts": 1681470000, "datetime": "2023/04/14 12:00:00", "import": 0.29324, "export": 0.0, "solar": 0.0, "consumed": 0.29324}
{"ts": 1681473600, "datetime": "2023/04/14 13:00:00", "import": 0.29723, "export": 0.0, "solar": 0.0, "consumed": 0.29723}
{"ts": 1681477200, "datetime": "2023/04/14 14:00:00", "import": 0.36334, "export": 0.0, "solar": 0.0, "consumed": 0.36334}
{"ts": 1681480800, "datetime": "2023/04/14 15:00:00", "import": 0.46093, "export": 0.0, "solar": 0.0, "consumed": 0.46093}
{"ts": 1681484400, "datetime": "2023/04/14 16:00:00", "import": 0.5444, "export": 0.0, "solar": 0.0, "consumed": 0.5444}
{"ts": 1681488000, "datetime": "2023/04/14 17:00:00", "import": 0.498, "export": 0.0, "solar": 0.0, "consumed": 0.498}
{"ts": 1681491600, "datetime": "2023/04/14 18:00:00", "import": 1.38172, "export": 0.0, "solar": 0.0, "consumed": 1.38172}
{"ts": 1681495200, "datetime": "2023/04/14 19:00:00", "import": 0.55653, "export": 0.0, "solar": 0.0, "consumed": 0.55653}
{"ts": 1681498800, "datetime": "2023/04/14 20:00:00", "import": 0.59554, "export": 0.0, "solar": 0.0, "consumed": 0.59554}
{"ts": 1681502400, "datetime": "2023/04/14 21:00:00", "import": 1.0932, "export": 0.0, "solar": 0.0, "consumed": 1.0932}
{"ts": 1681506000, "datetime": "2023/04/14 22:00:00", "import": 0.6666599999999999, "export": 0.0, "solar": 0.0, "consumed": 0.6666599999999999}
{"ts": 1681509600, "datetime": "2023/04/14 23:00:00", "import": 0.67061, "export": 0.0, "solar": 0.0, "consumed": 0.67061}
```

### Example CSV File
```csv
consumed,datetime,export,import,solar,ts
0.647,2023/04/14 00:00:00,0.0,0.647,0.0,1681426800
0.227,2023/04/14 01:00:00,0.0,0.227,0.0,1681430400
0.784,2023/04/14 02:00:00,0.0,0.784,0.0,1681434000
0.186,2023/04/14 03:00:00,0.0,0.186,0.0,1681437600
0.164,2023/04/14 04:00:00,0.0,0.164,0.0,1681441200
0.181,2023/04/14 05:00:00,0.0,0.181,0.0,1681444800
0.206,2023/04/14 06:00:00,0.0,0.206,0.0,1681448400
0.195,2023/04/14 07:00:00,0.0,0.195,0.0,1681452000
0.2,2023/04/14 08:00:00,0.0,0.2,0.0,1681455600
0.209,2023/04/14 09:00:00,0.0,0.209,0.0,1681459200
0.189,2023/04/14 10:00:00,0.0,0.189,0.0,1681462800
0.35,2023/04/14 11:00:00,0.0,0.35,0.0,1681466400
0.293,2023/04/14 12:00:00,0.0,0.293,0.0,1681470000
0.297,2023/04/14 13:00:00,0.0,0.297,0.0,1681473600
0.363,2023/04/14 14:00:00,0.0,0.363,0.0,1681477200
0.461,2023/04/14 15:00:00,0.0,0.461,0.0,1681480800
0.544,2023/04/14 16:00:00,0.0,0.544,0.0,1681484400
0.498,2023/04/14 17:00:00,0.0,0.498,0.0,1681488000
1.382,2023/04/14 18:00:00,0.0,1.382,0.0,1681491600
0.557,2023/04/14 19:00:00,0.0,0.557,0.0,1681495200
0.596,2023/04/14 20:00:00,0.0,0.596,0.0,1681498800
1.093,2023/04/14 21:00:00,0.0,1.093,0.0,1681502400
0.667,2023/04/14 22:00:00,0.0,0.667,0.0,1681506000
0.671,2023/04/14 23:00:00,0.0,0.671,0.0,1681509600
```
### Field Descriptions
* ts   
The EPOCH timestamp of the start of the consumption hour
* datetime   
A string datetime in YYYY/MM/DD HH:MM:SS in local time. The timezone for your device is retrieved in the Shelly API call
* import   
Import kWh units
* export   
Export kWh units
* solar   
Solar kWh units
* consumed   
Consumed kWh units
