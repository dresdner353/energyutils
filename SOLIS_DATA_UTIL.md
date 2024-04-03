# Solis Inverter Data Utility

The ```solis_data_util.py``` script is designed to retrieve inverter data from the Solis Cloud service. For this to be possible, you need to:
* Open a support ticket with Solis to enable API access and follow instructions they provide
* If you have a Solis string inverter that does not record grid import/export you may optionally enhance this retrieval with additonal data from a Shelly EM or Pro device:
   - The expected CT clamp wiring is to have the first CT input wired for Grid Import (positive) and export (negative)
   - The 2nd CT clamp is not used by this script (as solar data is provided by the Solis inverter)
   - Obtain a cloud API auth key from your Shelly account.
   - Obtain your Shelly EM device ID
   - Get the recommended Shelly Cloud hostname from your account

## Usage
```
usage: solis_data_util.py [-h] [--odir ODIR] [--days DAYS] --solis_inverter_sn
                          SOLIS_INVERTER_SN --solis_api_host SOLIS_API_HOST
                          --solis_key_id SOLIS_KEY_ID 
                          --solis_key_secret SOLIS_KEY_SECRET 
                          [--solis_strings {0,1,2,3,4,5,6,7,8}]
                          [--shelly_api_host SHELLY_API_HOST]
                          [--shelly_device_id SHELLY_DEVICE_ID]
                          [--shelly_auth_key SHELLY_AUTH_KEY] [--verbose]

Solis Inverter Data Retrieval Utility

optional arguments:
  -h, --help            show this help message and exit
  --odir ODIR           Output Directory for generated files
  --days DAYS           Backfill in days (def 30)
  --solis_inverter_sn SOLIS_INVERTER_SN
                        Solis Inverter Serial Number
  --solis_api_host SOLIS_API_HOST
                        Solis Inverter API Host
  --solis_key_id SOLIS_KEY_ID
                        Solis Inverter API Key ID
  --solis_key_secret SOLIS_KEY_SECRET
                        Solis Inverter API Key Secret
  --solis_strings {0,1,2,3,4,5,6,7,8}
                        Number of Separate Strings to track def:0 (disabled)
  --shelly_api_host SHELLY_API_HOST
                        Shelly API Host
  --shelly_device_id SHELLY_DEVICE_ID
                        Shelly Device ID
  --shelly_auth_key SHELLY_AUTH_KEY
                        Shelly API Auth Key
  --verbose             Enable verbose output

```

Options:
* --odir /path/to/store/JSONL files  
This specifies the directory to store the generated JSONL files. On subsequent invokes of the script, only new. partial or missing days are retrieved for efficiency.
* --days DAYS  
The number of backlog days to retrieve. Typically this should be set to something like 30 to allow the script go back an entire month to retrieve any missing data since the last invoke. On the first invoke, this might be set to larger value to retrieve everything since the inverter was first deployed.
* --solis_inverter_sn SOLIS_INVERTER_SN  
The Solis inverter serial number
* --solis_api_host SOLIS_API_HOST  
The Solis Cloud API host 
* --solis_key_id SOLIS_KEY_ID . 
The Solis API cloud key as given to you by Solis support
* --solis_key_secret SOLIS_KEY_SECRET  
The Solis API cloud secret as given to you by Solis support
* --solis_strings <num_strings>  
Optional number of separate strings to track. This defaults to 0 (disabled). If set to a value 1-8, it will try to additionally separate the reporting of solar generation into separate kWh values per hour per string. The fields are added in as "solar_pv1", "solar_pv2" etc in conjunction with the total "solar" value. It does this calculation using an averaging mechanism performed on the snapshot (kW) values that Solis provides in its 5-minute snapshots. So its not a rocket-proof calculation but statistically should be close.
* --shelly_api_host SHELLY_API_HOST  
Optional Shelly API host if you are using a Solis string inverter in conjunction with a Shelly EM/Pro
* --shelly_device_id SHELLY_DEVICE_ID  
Optional Shelly Cloud device ID
* --shelly_auth_key SHELLY_AUTH_KEY  
Optional Shelly Cloud auth key

## Operation
* Retrieval acts incrementally, only pulling data for day files you do not already have. 
* Incomplete days are also detected by means of a "partial" property in the file and pulled again automatically
  - When recording data for the current day (today), the file records are marked with a "partial" Boolean property
  - If such files are detected when checking for existing data, the full day is retrieved again
  - This will ensure imcomplete data is fully retrieved when possible


## Example Run for Solis Hybrid inverter
```
% python3 solis_data_util.py \
        --days 30 \
        --solis_api_host https://www.soliscloud.com:13333 \
        --solis_key_id XXXXXXXXXXXXXXXXXXX \
        --solis_key_secret XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
        --solis_inverter_sn XXXXXXXXXXXXXXX \
        --odir '/somewhere/my_data'

Thu Jan 25 18:47:38 2024 Updating /somewhere/my_data/2024-01-25.jsonl
Thu Jan 25 18:47:41 2024 Writing /somewhere/my_data/2024-01-24.jsonl
Thu Jan 25 18:47:45 2024 Writing /somewhere/my_data/2024-01-23.jsonl
```

## Example File
```json
{"datetime": "2024/01/24 00:00:00", "ts": 1706054660, "solar": 0, "import": 0.10000, "export": 0, "consumed": 0.20000, "solar_consumed": 0, "hour": 0, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0}
{"datetime": "2024/01/24 01:00:00", "ts": 1706058296, "solar": 0, "import": 0.10000, "export": 0, "consumed": 0.10000, "solar_consumed": 0, "hour": 1, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 02:00:00", "ts": 1706061630, "solar": 0, "import": 0.10000, "export": 0, "consumed": 0.20000, "solar_consumed": 0, "hour": 2, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 03:00:00", "ts": 1706065266, "solar": 0, "import": 0.10000, "export": 0, "consumed": 0.10000, "solar_consumed": 0, "hour": 3, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 04:00:00", "ts": 1706068903, "solar": 0, "import": 0.20000, "export": 0, "consumed": 0.10000, "solar_consumed": 0, "hour": 4, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 05:00:00", "ts": 1706072541, "solar": 0, "import": 0.10000, "export": 0, "consumed": 0.10000, "solar_consumed": 0, "hour": 5, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 06:00:00", "ts": 1706076177, "solar": 0, "import": 0.30000, "export": 0, "consumed": 0.40000, "solar_consumed": 0, "hour": 6, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 07:00:00", "ts": 1706079852, "solar": 0, "import": 0.40000, "export": 0, "consumed": 0.40000, "solar_consumed": 0, "hour": 7, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 08:00:00", "ts": 1706083476, "solar": 0.10000, "import": 0.80000, "export": 0, "consumed": 0.90000, "solar_consumed": 0.10000, "hour": 8, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 09:00:00", "ts": 1706086805, "solar": 0.00000, "import": 0.20000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.00000, "hour": 9, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 10:00:00", "ts": 1706090439, "solar": 0.20000, "import": 0.10000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.20000, "hour": 10, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.10000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 11:00:00", "ts": 1706094071, "solar": 0.50000, "import": 0.00000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.50000, "hour": 11, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.20000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 12:00:00", "ts": 1706097702, "solar": 0.30000, "import": 0.00000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.30000, "hour": 12, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.20000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 13:00:00", "ts": 1706101334, "solar": 0.40000, "import": 0.00000, "export": 0, "consumed": 0.40000, "solar_consumed": 0.40000, "hour": 13, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.20000, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 14:00:00", "ts": 1706104966, "solar": 0.40000, "import": 0.00000, "export": 0, "consumed": 0.30000, "solar_consumed": 0.40000, "hour": 14, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.20000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 15:00:00", "ts": 1706108598, "solar": 0.20000, "import": 0.00000, "export": 0, "consumed": 0.10000, "solar_consumed": 0.20000, "hour": 15, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 16:00:00", "ts": 1706112276, "solar": 0.00000, "import": 0.00000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.00000, "hour": 16, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 17:00:00", "ts": 1706115891, "solar": 0.00000, "import": 0.00000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.00000, "hour": 17, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.30000}
{"datetime": "2024/01/24 18:00:00", "ts": 1706119220, "solar": 0.00000, "import": 1.40000, "export": 0, "consumed": 1.60000, "solar_consumed": 0.00000, "hour": 18, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 19:00:00", "ts": 1706122852, "solar": 0.00000, "import": 0.30000, "export": 0, "consumed": 0.20000, "solar_consumed": 0.00000, "hour": 19, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 20:00:00", "ts": 1706126485, "solar": 0.00000, "import": 0.40000, "export": 0, "consumed": 0.50000, "solar_consumed": 0.00000, "hour": 20, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.10000}
{"datetime": "2024/01/24 21:00:00", "ts": 1706130119, "solar": 0.00000, "import": 1.10000, "export": 0, "consumed": 1.10000, "solar_consumed": 0.00000, "hour": 21, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 22:00:00", "ts": 1706133751, "solar": 0.00000, "import": 0.50000, "export": 0, "consumed": 0.40000, "solar_consumed": 0.00000, "hour": 22, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.00000}
{"datetime": "2024/01/24 23:00:00", "ts": 1706137416, "solar": 0.00000, "import": 0.00000, "export": 0, "consumed": 0.10000, "solar_consumed": 0.00000, "hour": 23, "day": "2024-01-24", "month": "2024-01", "year": "2024", "weekday": "3 Wed", "week": "2024-04", "battery_charge": 0.00000, "battery_discharge": 0.00000}
```
