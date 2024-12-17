# SEMOpx Market Data Utility

SEMOpx provides day-ahead and intra-day electricity market trading for the Republic of Ireland and Northern Ireland as part of the Single Electricity Market (SEM).

Power auctions are run in several forms varying from day-ahead to three separate intra-day auctions. The data in relation to these auctions is made available via reports from the [semopx.com](https://semopx.com) website and also via their API.

This script implements the SEMOpx API and specifically targets the day-ahead (DA) data. When invoked, the script calls the API to first collect data on available DA reports for the specified ROI or NI market and then pulls that report data per given day. The data is converted from the SEMOpx format and written to JSONL files stored in a target directory. 

## Usage
```
usage: semopx_data_util.py [-h] [--odir ODIR] [--days DAYS] [--market {ROI-DA,NI-DA}] [--timezone TIMEZONE]
                           [--verbose]

SEMOpx Data Retrieval Utility

options:
  -h, --help            show this help message and exit
  --odir ODIR           Output Directory for generated files
  --days DAYS           Backfill days (def 5)
  --market {ROI-DA,NI-DA}
                        Market Area (def ROI-DA)
  --timezone TIMEZONE   Timezone def:Europe/Dublin
  --verbose             Enable verbose output
```

Options:
* --odir /path/to/output/directory  
This specifies the output directory for the retrieved data. Each day is written to a separate JSONL file.
* --days DAYS   
This is the number of days backlog to retrieve. The default is the last 5 days. SEMOpx only store data for about 1 year and as such this script could be run to pull back data for all available days by setting the --days option to a high number. 
* --market MARKET  
The market can be one of two values only.. ROI-DA or NI-DA. If a user wanted to track prices for both markets, you could separately invoke the script, each with a separate --odir and --market value
* --timezone TIMEZONE  
Allows for specifying of a timezone. The default is Europe/Dublin and should be fine for any processing within ROI/NI. 

## Operation
* Retrieval acts incrementally, only pulling data for day files you do not already have. 
* So it you invoke the script with --days 100, it will use the API to get and write files for the last 100 days
* If you immediately re-run the script, it will compute the last 100 reports but not retrieve any data after discovering that the files already exist in the --odir location.
* This allows for incremental usage of the script on a daily basis, including handling of gaps if the script were not run for some time.
* The data is written in JSONL files, one per day
* Each line in a file is the GBP & Euro mWh trading price for a given hour in the day. 
* Prices are also shown in kWh for convenience.
* Time is presented in both EPOCH format (UTC seconds in 1970-01-01) and in local string format (YYYY/MM/DD HH:MM:SS) based on the selected timezone


## Example Call
```
python3 semopx_data_util.py --days 10 --market ROI-DA --odir Desktop/semopx_data
Mon Dec 16 14:20:59 2024 Retrieving DA report details for days:10
Mon Dec 16 14:21:00 2024 Retrieving report page 1/0 (reports:0)
Mon Dec 16 14:21:02 2024 Writing.. Desktop/semopx_data/2024-12-17.jsonl
Mon Dec 16 14:21:03 2024 Writing.. Desktop/semopx_data/2024-12-16.jsonl
Mon Dec 16 14:21:04 2024 Writing.. Desktop/semopx_data/2024-12-15.jsonl
Mon Dec 16 14:21:05 2024 Writing.. Desktop/semopx_data/2024-12-14.jsonl
Mon Dec 16 14:21:06 2024 Writing.. Desktop/semopx_data/2024-12-13.jsonl
Mon Dec 16 14:21:08 2024 Writing.. Desktop/semopx_data/2024-12-12.jsonl
Mon Dec 16 14:21:09 2024 Writing.. Desktop/semopx_data/2024-12-11.jsonl
Mon Dec 16 14:21:10 2024 Writing.. Desktop/semopx_data/2024-12-10.jsonl
Mon Dec 16 14:21:11 2024 Writing.. Desktop/semopx_data/2024-12-09.jsonl
Mon Dec 16 14:21:13 2024 Writing.. Desktop/semopx_data/2024-12-08.jsonl
Mon Dec 16 14:21:13 2024 Done.. retrieved 10/10 reports, skipped 0
```

## Sample File
```json
{"ts": 1734303600, "datetime": "2024/12/15 23:00:00", "market_area": "ROI-DA", "mwh_euro": 17.7900, "kwh_euro": 0.0178, "mwh_gbp": 14.8500, "kwh_gbp": 0.0149}
{"ts": 1734307200, "datetime": "2024/12/16 00:00:00", "market_area": "ROI-DA", "mwh_euro": 19, "kwh_euro": 0.0190, "mwh_gbp": 15.8640, "kwh_gbp": 0.0159}
{"ts": 1734310800, "datetime": "2024/12/16 01:00:00", "market_area": "ROI-DA", "mwh_euro": 12, "kwh_euro": 0.0120, "mwh_gbp": 10.0190, "kwh_gbp": 0.0100}
{"ts": 1734314400, "datetime": "2024/12/16 02:00:00", "market_area": "ROI-DA", "mwh_euro": 12.3400, "kwh_euro": 0.0123, "mwh_gbp": 10.3000, "kwh_gbp": 0.0103}
{"ts": 1734318000, "datetime": "2024/12/16 03:00:00", "market_area": "ROI-DA", "mwh_euro": 12.7900, "kwh_euro": 0.0128, "mwh_gbp": 10.6790, "kwh_gbp": 0.0107}
{"ts": 1734321600, "datetime": "2024/12/16 04:00:00", "market_area": "ROI-DA", "mwh_euro": 13.9100, "kwh_euro": 0.0139, "mwh_gbp": 11.6100, "kwh_gbp": 0.0116}
{"ts": 1734325200, "datetime": "2024/12/16 05:00:00", "market_area": "ROI-DA", "mwh_euro": 34.7300, "kwh_euro": 0.0347, "mwh_gbp": 29, "kwh_gbp": 0.0290}
{"ts": 1734328800, "datetime": "2024/12/16 06:00:00", "market_area": "ROI-DA", "mwh_euro": 85, "kwh_euro": 0.0850, "mwh_gbp": 70.9690, "kwh_gbp": 0.0710}
{"ts": 1734332400, "datetime": "2024/12/16 07:00:00", "market_area": "ROI-DA", "mwh_euro": 103.9000, "kwh_euro": 0.1039, "mwh_gbp": 86.7500, "kwh_gbp": 0.0867}
{"ts": 1734336000, "datetime": "2024/12/16 08:00:00", "market_area": "ROI-DA", "mwh_euro": 111.2300, "kwh_euro": 0.1112, "mwh_gbp": 92.8700, "kwh_gbp": 0.0929}
{"ts": 1734339600, "datetime": "2024/12/16 09:00:00", "market_area": "ROI-DA", "mwh_euro": 110.1900, "kwh_euro": 0.1102, "mwh_gbp": 92.0010, "kwh_gbp": 0.0920}
{"ts": 1734343200, "datetime": "2024/12/16 10:00:00", "market_area": "ROI-DA", "mwh_euro": 104.3300, "kwh_euro": 0.1043, "mwh_gbp": 87.1090, "kwh_gbp": 0.0871}
{"ts": 1734346800, "datetime": "2024/12/16 11:00:00", "market_area": "ROI-DA", "mwh_euro": 102.0600, "kwh_euro": 0.1021, "mwh_gbp": 85.2130, "kwh_gbp": 0.0852}
{"ts": 1734350400, "datetime": "2024/12/16 12:00:00", "market_area": "ROI-DA", "mwh_euro": 98.7300, "kwh_euro": 0.0987, "mwh_gbp": 82.4330, "kwh_gbp": 0.0824}
{"ts": 1734354000, "datetime": "2024/12/16 13:00:00", "market_area": "ROI-DA", "mwh_euro": 97.9000, "kwh_euro": 0.0979, "mwh_gbp": 81.7400, "kwh_gbp": 0.0817}
{"ts": 1734357600, "datetime": "2024/12/16 14:00:00", "market_area": "ROI-DA", "mwh_euro": 103.9000, "kwh_euro": 0.1039, "mwh_gbp": 86.7500, "kwh_gbp": 0.0867}
{"ts": 1734361200, "datetime": "2024/12/16 15:00:00", "market_area": "ROI-DA", "mwh_euro": 111, "kwh_euro": 0.1110, "mwh_gbp": 92.6780, "kwh_gbp": 0.0927}
{"ts": 1734364800, "datetime": "2024/12/16 16:00:00", "market_area": "ROI-DA", "mwh_euro": 149.2000, "kwh_euro": 0.1492, "mwh_gbp": 124.5720, "kwh_gbp": 0.1246}
{"ts": 1734368400, "datetime": "2024/12/16 17:00:00", "market_area": "ROI-DA", "mwh_euro": 177.4500, "kwh_euro": 0.1774, "mwh_gbp": 148.1590, "kwh_gbp": 0.1482}
{"ts": 1734372000, "datetime": "2024/12/16 18:00:00", "market_area": "ROI-DA", "mwh_euro": 175, "kwh_euro": 0.1750, "mwh_gbp": 146.1130, "kwh_gbp": 0.1461}
{"ts": 1734375600, "datetime": "2024/12/16 19:00:00", "market_area": "ROI-DA", "mwh_euro": 160, "kwh_euro": 0.1600, "mwh_gbp": 133.5890, "kwh_gbp": 0.1336}
{"ts": 1734379200, "datetime": "2024/12/16 20:00:00", "market_area": "ROI-DA", "mwh_euro": 150.7900, "kwh_euro": 0.1508, "mwh_gbp": 125.9000, "kwh_gbp": 0.1259}
{"ts": 1734382800, "datetime": "2024/12/16 21:00:00", "market_area": "ROI-DA", "mwh_euro": 127.4900, "kwh_euro": 0.1275, "mwh_gbp": 106.4460, "kwh_gbp": 0.1064}
{"ts": 1734386400, "datetime": "2024/12/16 22:00:00", "market_area": "ROI-DA", "mwh_euro": 120.0200, "kwh_euro": 0.1200, "mwh_gbp": 100.2090, "kwh_gbp": 0.1002}
```

## Daylight Savings Scenarios
SEMOpx times are strictly in UTC format when published. To allow for both a UTC and local time mindset, each record contains a "ts" field and "datetime" field. The "ts" field is a epoch value and the "datetime" represents the converted local time. 

Under normal circumstances, each JSONL file will contain 24 lines, one line per hour, starting 23:00 on the night before to 22:00 on the following night. However in DST change days, the number of lines will vary to just 23 in spring when the clocks jump forward, skipping an hour and 25 lines in winter when the clock rolls back and repeats an hour.

The following examples highlight this behaviour:

### March 31st 2024 (day is 23 hours long, 1AM skipped)
```json
{"ts": 1711839600, "datetime": "2024/03/30 23:00:00", "market_area": "ROI-DA", "mwh_euro": 94.6000, "kwh_euro": 0.0946, "mwh_gbp": 80.9930, "kwh_gbp": 0.0810}
{"ts": 1711843200, "datetime": "2024/03/31 00:00:00", "market_area": "ROI-DA", "mwh_euro": 94.5000, "kwh_euro": 0.0945, "mwh_gbp": 80.9100, "kwh_gbp": 0.0809}
{"ts": 1711846800, "datetime": "2024/03/31 02:00:00", "market_area": "ROI-DA", "mwh_euro": 82.8100, "kwh_euro": 0.0828, "mwh_gbp": 70.9000, "kwh_gbp": 0.0709}
{"ts": 1711850400, "datetime": "2024/03/31 03:00:00", "market_area": "ROI-DA", "mwh_euro": 82.0100, "kwh_euro": 0.0820, "mwh_gbp": 70.2140, "kwh_gbp": 0.0702}
{"ts": 1711854000, "datetime": "2024/03/31 04:00:00", "market_area": "ROI-DA", "mwh_euro": 79, "kwh_euro": 0.0790, "mwh_gbp": 67.6370, "kwh_gbp": 0.0676}
{"ts": 1711857600, "datetime": "2024/03/31 05:00:00", "market_area": "ROI-DA", "mwh_euro": 70.1500, "kwh_euro": 0.0702, "mwh_gbp": 60.0600, "kwh_gbp": 0.0601}
{"ts": 1711861200, "datetime": "2024/03/31 06:00:00", "market_area": "ROI-DA", "mwh_euro": 71.1000, "kwh_euro": 0.0711, "mwh_gbp": 60.8730, "kwh_gbp": 0.0609}
{"ts": 1711864800, "datetime": "2024/03/31 07:00:00", "market_area": "ROI-DA", "mwh_euro": 73.8700, "kwh_euro": 0.0739, "mwh_gbp": 63.2450, "kwh_gbp": 0.0632}
{"ts": 1711868400, "datetime": "2024/03/31 08:00:00", "market_area": "ROI-DA", "mwh_euro": 78.0700, "kwh_euro": 0.0781, "mwh_gbp": 66.8410, "kwh_gbp": 0.0668}
{"ts": 1711872000, "datetime": "2024/03/31 09:00:00", "market_area": "ROI-DA", "mwh_euro": 82.4300, "kwh_euro": 0.0824, "mwh_gbp": 70.5700, "kwh_gbp": 0.0706}
{"ts": 1711875600, "datetime": "2024/03/31 10:00:00", "market_area": "ROI-DA", "mwh_euro": 78.8400, "kwh_euro": 0.0788, "mwh_gbp": 67.5000, "kwh_gbp": 0.0675}
{"ts": 1711879200, "datetime": "2024/03/31 11:00:00", "market_area": "ROI-DA", "mwh_euro": 73.1500, "kwh_euro": 0.0732, "mwh_gbp": 62.6280, "kwh_gbp": 0.0626}
{"ts": 1711882800, "datetime": "2024/03/31 12:00:00", "market_area": "ROI-DA", "mwh_euro": 69, "kwh_euro": 0.0690, "mwh_gbp": 59.0750, "kwh_gbp": 0.0591}
{"ts": 1711886400, "datetime": "2024/03/31 13:00:00", "market_area": "ROI-DA", "mwh_euro": 65.2000, "kwh_euro": 0.0652, "mwh_gbp": 55.8220, "kwh_gbp": 0.0558}
{"ts": 1711890000, "datetime": "2024/03/31 14:00:00", "market_area": "ROI-DA", "mwh_euro": 65.2000, "kwh_euro": 0.0652, "mwh_gbp": 55.8220, "kwh_gbp": 0.0558}
{"ts": 1711893600, "datetime": "2024/03/31 15:00:00", "market_area": "ROI-DA", "mwh_euro": 66.9000, "kwh_euro": 0.0669, "mwh_gbp": 57.2770, "kwh_gbp": 0.0573}
{"ts": 1711897200, "datetime": "2024/03/31 16:00:00", "market_area": "ROI-DA", "mwh_euro": 72.4500, "kwh_euro": 0.0725, "mwh_gbp": 62.0290, "kwh_gbp": 0.0620}
{"ts": 1711900800, "datetime": "2024/03/31 17:00:00", "market_area": "ROI-DA", "mwh_euro": 93.4400, "kwh_euro": 0.0934, "mwh_gbp": 80, "kwh_gbp": 0.0800}
{"ts": 1711904400, "datetime": "2024/03/31 18:00:00", "market_area": "ROI-DA", "mwh_euro": 111.3500, "kwh_euro": 0.1113, "mwh_gbp": 95.3340, "kwh_gbp": 0.0953}
{"ts": 1711908000, "datetime": "2024/03/31 19:00:00", "market_area": "ROI-DA", "mwh_euro": 125, "kwh_euro": 0.1250, "mwh_gbp": 107.0210, "kwh_gbp": 0.1070}
{"ts": 1711911600, "datetime": "2024/03/31 20:00:00", "market_area": "ROI-DA", "mwh_euro": 120.5100, "kwh_euro": 0.1205, "mwh_gbp": 103.1760, "kwh_gbp": 0.1032}
{"ts": 1711915200, "datetime": "2024/03/31 21:00:00", "market_area": "ROI-DA", "mwh_euro": 100, "kwh_euro": 0.1000, "mwh_gbp": 85.6160, "kwh_gbp": 0.0856}
{"ts": 1711918800, "datetime": "2024/03/31 22:00:00", "market_area": "ROI-DA", "mwh_euro": 80.1000, "kwh_euro": 0.0801, "mwh_gbp": 68.5790, "kwh_gbp": 0.0686}
```

### October 27th 2024 (day is 25 hours long, two 1AM periods)
```json
{"ts": 1729980000, "datetime": "2024/10/26 23:00:00", "market_area": "ROI-DA", "mwh_euro": 171.1100, "kwh_euro": 0.1711, "mwh_gbp": 142.5440, "kwh_gbp": 0.1425}
{"ts": 1729983600, "datetime": "2024/10/27 00:00:00", "market_area": "ROI-DA", "mwh_euro": 180.2000, "kwh_euro": 0.1802, "mwh_gbp": 150.1170, "kwh_gbp": 0.1501}
{"ts": 1729987200, "datetime": "2024/10/27 01:00:00", "market_area": "ROI-DA", "mwh_euro": 196.2000, "kwh_euro": 0.1962, "mwh_gbp": 163.4460, "kwh_gbp": 0.1634}
{"ts": 1729990800, "datetime": "2024/10/27 01:00:00", "market_area": "ROI-DA", "mwh_euro": 203, "kwh_euro": 0.2030, "mwh_gbp": 169.1100, "kwh_gbp": 0.1691}
{"ts": 1729994400, "datetime": "2024/10/27 02:00:00", "market_area": "ROI-DA", "mwh_euro": 163.6000, "kwh_euro": 0.1636, "mwh_gbp": 136.2880, "kwh_gbp": 0.1363}
{"ts": 1729998000, "datetime": "2024/10/27 03:00:00", "market_area": "ROI-DA", "mwh_euro": 137.9300, "kwh_euro": 0.1379, "mwh_gbp": 114.9000, "kwh_gbp": 0.1149}
{"ts": 1730001600, "datetime": "2024/10/27 04:00:00", "market_area": "ROI-DA", "mwh_euro": 115.4500, "kwh_euro": 0.1154, "mwh_gbp": 96.1760, "kwh_gbp": 0.0962}
{"ts": 1730005200, "datetime": "2024/10/27 05:00:00", "market_area": "ROI-DA", "mwh_euro": 122.0100, "kwh_euro": 0.1220, "mwh_gbp": 101.6410, "kwh_gbp": 0.1016}
{"ts": 1730008800, "datetime": "2024/10/27 06:00:00", "market_area": "ROI-DA", "mwh_euro": 148.4500, "kwh_euro": 0.1484, "mwh_gbp": 123.6670, "kwh_gbp": 0.1237}
{"ts": 1730012400, "datetime": "2024/10/27 07:00:00", "market_area": "ROI-DA", "mwh_euro": 106.4500, "kwh_euro": 0.1065, "mwh_gbp": 88.6790, "kwh_gbp": 0.0887}
{"ts": 1730016000, "datetime": "2024/10/27 08:00:00", "market_area": "ROI-DA", "mwh_euro": 110.0700, "kwh_euro": 0.1101, "mwh_gbp": 91.6940, "kwh_gbp": 0.0917}
{"ts": 1730019600, "datetime": "2024/10/27 09:00:00", "market_area": "ROI-DA", "mwh_euro": 102, "kwh_euro": 0.1020, "mwh_gbp": 84.9720, "kwh_gbp": 0.0850}
{"ts": 1730023200, "datetime": "2024/10/27 10:00:00", "market_area": "ROI-DA", "mwh_euro": 100.8900, "kwh_euro": 0.1009, "mwh_gbp": 84.0470, "kwh_gbp": 0.0840}
{"ts": 1730026800, "datetime": "2024/10/27 11:00:00", "market_area": "ROI-DA", "mwh_euro": 95, "kwh_euro": 0.0950, "mwh_gbp": 79.1400, "kwh_gbp": 0.0791}
{"ts": 1730030400, "datetime": "2024/10/27 12:00:00", "market_area": "ROI-DA", "mwh_euro": 93.4800, "kwh_euro": 0.0935, "mwh_gbp": 77.8740, "kwh_gbp": 0.0779}
{"ts": 1730034000, "datetime": "2024/10/27 13:00:00", "market_area": "ROI-DA", "mwh_euro": 100.3000, "kwh_euro": 0.1003, "mwh_gbp": 83.5550, "kwh_gbp": 0.0836}
{"ts": 1730037600, "datetime": "2024/10/27 14:00:00", "market_area": "ROI-DA", "mwh_euro": 96.0100, "kwh_euro": 0.0960, "mwh_gbp": 79.9820, "kwh_gbp": 0.0800}
{"ts": 1730041200, "datetime": "2024/10/27 15:00:00", "market_area": "ROI-DA", "mwh_euro": 102.0300, "kwh_euro": 0.1020, "mwh_gbp": 85, "kwh_gbp": 0.0850}
{"ts": 1730044800, "datetime": "2024/10/27 16:00:00", "market_area": "ROI-DA", "mwh_euro": 128.0100, "kwh_euro": 0.1280, "mwh_gbp": 106.6390, "kwh_gbp": 0.1066}
{"ts": 1730048400, "datetime": "2024/10/27 17:00:00", "market_area": "ROI-DA", "mwh_euro": 140.4300, "kwh_euro": 0.1404, "mwh_gbp": 116.9860, "kwh_gbp": 0.1170}
{"ts": 1730052000, "datetime": "2024/10/27 18:00:00", "market_area": "ROI-DA", "mwh_euro": 120.5600, "kwh_euro": 0.1206, "mwh_gbp": 100.4300, "kwh_gbp": 0.1004}
{"ts": 1730055600, "datetime": "2024/10/27 19:00:00", "market_area": "ROI-DA", "mwh_euro": 110, "kwh_euro": 0.1100, "mwh_gbp": 91.6360, "kwh_gbp": 0.0916}
{"ts": 1730059200, "datetime": "2024/10/27 20:00:00", "market_area": "ROI-DA", "mwh_euro": 101.3000, "kwh_euro": 0.1013, "mwh_gbp": 84.3890, "kwh_gbp": 0.0844}
{"ts": 1730062800, "datetime": "2024/10/27 21:00:00", "market_area": "ROI-DA", "mwh_euro": 92.0100, "kwh_euro": 0.0920, "mwh_gbp": 76.6490, "kwh_gbp": 0.0766}
{"ts": 1730066400, "datetime": "2024/10/27 22:00:00", "market_area": "ROI-DA", "mwh_euro": 80.0800, "kwh_euro": 0.0801, "mwh_gbp": 66.7110, "kwh_gbp": 0.0667}
```
