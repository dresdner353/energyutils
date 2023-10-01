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
usage: shelly_em_data_util.py [-h] --host HOST [--odir ODIR] [--days DAYS] --id
                              ID --auth_key AUTH_KEY [--verbose]

Shelly EM Data Retrieval Utility

optional arguments:
  -h, --help           show this help message and exit
  --host HOST          Shelly API Host
  --odir ODIR          Output Directory for generated files
  --days DAYS          Backfill in days (def 30)
  --id ID              Device ID
  --auth_key AUTH_KEY  API Auth Key
  --verbose            Enable verbose output
```
Notes:
* The API host is set by the --host arg. 
* The --auth_key is the API key you retrieved from your account
* The --id option sets the device ID to query
* The output directory is set by --odir but this also defaults to ~/.shellyemdata
* The --days option sets the number of full days to retrieve from today
* Retrieval acts incrementally, only pulling data for day files you do not already have. 
* Incomplete days are also detected by means of a "partial" property in the file and pulled again automatically
  - When recording data for the current day (today), the file records are marked with a "partial" Boolean property
  - If such files are detected when checking for existing data, the full day is retrieved again
  - This will ensure imcomplete data is fully retrieved when possible

## Example Run
```
% python3  work/energyutils/shelly_em_data_util.py \
        --host shelly-XX-eu.shelly.cloud \
        --id XXXXXXXXXXXX \
        --auth_key XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
        --odir /path/to/somewhere \
        --days 10

......
Mon May 15 19:17:29 2023 Getting data for 2023-03-23 00:00:00
Mon May 15 19:17:30 2023 Writing to /path/to/somewhere/2023-03-23.jsonl
Mon May 15 19:17:30 2023 Getting data for 2023-03-22 00:00:00
Mon May 15 19:17:30 2023 Writing to /path/to/somewhere/2023-03-22.jsonl
Mon May 15 19:17:30 2023 Getting data for 2023-03-21 00:00:00
Mon May 15 19:17:30 2023 Writing to /path/to/somewhere/2023-03-21.jsonl
Mon May 15 19:17:30 2023 Getting data for 2023-03-20 00:00:00
Mon May 15 19:17:31 2023 Writing to /path/to/somewhere/2023-03-20.jsonl
......
```

## Example File
```json
{"ts": 1679184000, "datetime": "2023/03/19 00:00:00", "import": 0.0000, "export": 0.0000, "hour": 0, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679187600, "datetime": "2023/03/19 01:00:00", "import": 0.0000, "export": 0.0000, "hour": 1, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679191200, "datetime": "2023/03/19 02:00:00", "import": 0.0000, "export": 0.0000, "hour": 2, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679194800, "datetime": "2023/03/19 03:00:00", "import": 0.0000, "export": 0.0000, "hour": 3, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679198400, "datetime": "2023/03/19 04:00:00", "import": 0.0000, "export": 0.0000, "hour": 4, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679202000, "datetime": "2023/03/19 05:00:00", "import": 0.0000, "export": 0.0000, "hour": 5, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679205600, "datetime": "2023/03/19 06:00:00", "import": 0.0000, "export": 0.0000, "hour": 6, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679209200, "datetime": "2023/03/19 07:00:00", "import": 0.0000, "export": 0.0000, "hour": 7, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679212800, "datetime": "2023/03/19 08:00:00", "import": 0.0000, "export": 0.0000, "hour": 8, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679216400, "datetime": "2023/03/19 09:00:00", "import": 0.0000, "export": 0.0000, "hour": 9, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679220000, "datetime": "2023/03/19 10:00:00", "import": 0.0000, "export": 0.0000, "hour": 10, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679223600, "datetime": "2023/03/19 11:00:00", "import": 0.0000, "export": 0.0000, "hour": 11, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679227200, "datetime": "2023/03/19 12:00:00", "import": 0.0000, "export": 0.0000, "hour": 12, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679230800, "datetime": "2023/03/19 13:00:00", "import": 0.0000, "export": 0.0000, "hour": 13, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679234400, "datetime": "2023/03/19 14:00:00", "import": 0.0000, "export": 0.0000, "hour": 14, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679238000, "datetime": "2023/03/19 15:00:00", "import": 0.0000, "export": 0.0000, "hour": 15, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679241600, "datetime": "2023/03/19 16:00:00", "import": 0.0000, "export": 0.0000, "hour": 16, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679245200, "datetime": "2023/03/19 17:00:00", "import": 0.0000, "export": 0.0000, "hour": 17, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679248800, "datetime": "2023/03/19 18:00:00", "import": 0.0000, "export": 0.0000, "hour": 18, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679252400, "datetime": "2023/03/19 19:00:00", "import": 0.0000, "export": 0.0000, "hour": 19, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679256000, "datetime": "2023/03/19 20:00:00", "import": 0.0000, "export": 0.0000, "hour": 20, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679259600, "datetime": "2023/03/19 21:00:00", "import": 0.0000, "export": 0.0000, "hour": 21, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679263200, "datetime": "2023/03/19 22:00:00", "import": 0.0000, "export": 0.0000, "hour": 22, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
{"ts": 1679266800, "datetime": "2023/03/19 23:00:00", "import": 0.0000, "export": 0.0000, "hour": 23, "day": "2023-03-19", "month": "2023-03", "year": "2023", "weekday": "7 Sun", "week": "2023-11", "solar": 0.0000, "consumed": 0.0000, "solar_consumed": 0.0000}
```
