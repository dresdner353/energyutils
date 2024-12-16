# SEMOpx Market Data Utility

SEMOpx provides day-ahead and intra-day electricity market trading for Ireland and Northern Ireland as part of the Single Electricity Market (SEM).

Power auctions are run in several forms varying from Day-ahead to three separate intra-day auctions. The data in relation to these auctions is made available via reports from the [semopx.com](https://semopx.com) website and also via their API.

This script implements the SMOpx API and specifically targets the day-ahead (DA) data. The script calls the SEMOpx API to first collect data on available DA reports for the specified ROI or NI market and then pulls that report data per given day. The data is reformatted and written to JSONL files stored in a target directory. 

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
* Each line in a file is the GBP & Euro trading price for a given hour in the day.
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
{"ts": 1734390000, "datetime": "2024/12/16 23:00:00", "market_area": "ROI-DA", "euro": 124, "gbp": 103.076}
{"ts": 1734393600, "datetime": "2024/12/17 00:00:00", "market_area": "ROI-DA", "euro": 97.13, "gbp": 80.74}
{"ts": 1734397200, "datetime": "2024/12/17 01:00:00", "market_area": "ROI-DA", "euro": 92.36, "gbp": 76.775}
{"ts": 1734400800, "datetime": "2024/12/17 02:00:00", "market_area": "ROI-DA", "euro": 89.74, "gbp": 74.6}
{"ts": 1734404400, "datetime": "2024/12/17 03:00:00", "market_area": "ROI-DA", "euro": 86.06, "gbp": 71.538}
{"ts": 1734408000, "datetime": "2024/12/17 04:00:00", "market_area": "ROI-DA", "euro": 86.06, "gbp": 71.538}
{"ts": 1734411600, "datetime": "2024/12/17 05:00:00", "market_area": "ROI-DA", "euro": 96.12, "gbp": 79.9}
{"ts": 1734415200, "datetime": "2024/12/17 06:00:00", "market_area": "ROI-DA", "euro": 107.34, "gbp": 89.227}
{"ts": 1734418800, "datetime": "2024/12/17 07:00:00", "market_area": "ROI-DA", "euro": 126.7, "gbp": 105.32}
{"ts": 1734422400, "datetime": "2024/12/17 08:00:00", "market_area": "ROI-DA", "euro": 132.5, "gbp": 110.14}
{"ts": 1734426000, "datetime": "2024/12/17 09:00:00", "market_area": "ROI-DA", "euro": 129.82, "gbp": 107.914}
{"ts": 1734429600, "datetime": "2024/12/17 10:00:00", "market_area": "ROI-DA", "euro": 117.07, "gbp": 97.315}
{"ts": 1734433200, "datetime": "2024/12/17 11:00:00", "market_area": "ROI-DA", "euro": 106.96, "gbp": 88.911}
{"ts": 1734436800, "datetime": "2024/12/17 12:00:00", "market_area": "ROI-DA", "euro": 104.44, "gbp": 86.816}
{"ts": 1734440400, "datetime": "2024/12/17 13:00:00", "market_area": "ROI-DA", "euro": 103.23, "gbp": 85.81}
{"ts": 1734444000, "datetime": "2024/12/17 14:00:00", "market_area": "ROI-DA", "euro": 102, "gbp": 84.788}
{"ts": 1734447600, "datetime": "2024/12/17 15:00:00", "market_area": "ROI-DA", "euro": 110, "gbp": 91.438}
{"ts": 1734451200, "datetime": "2024/12/17 16:00:00", "market_area": "ROI-DA", "euro": 119, "gbp": 98.919}
{"ts": 1734454800, "datetime": "2024/12/17 17:00:00", "market_area": "ROI-DA", "euro": 119, "gbp": 98.919}
{"ts": 1734458400, "datetime": "2024/12/17 18:00:00", "market_area": "ROI-DA", "euro": 105, "gbp": 87.282}
{"ts": 1734462000, "datetime": "2024/12/17 19:00:00", "market_area": "ROI-DA", "euro": 101.24, "gbp": 84.16}
{"ts": 1734465600, "datetime": "2024/12/17 20:00:00", "market_area": "ROI-DA", "euro": 95.94, "gbp": 79.751}
{"ts": 1734469200, "datetime": "2024/12/17 21:00:00", "market_area": "ROI-DA", "euro": 90, "gbp": 74.813}
{"ts": 1734472800, "datetime": "2024/12/17 22:00:00", "market_area": "ROI-DA", "euro": 57.73, "gbp": 47.988}
```

## Daylight Savings Scenarios
SEMOpx times are strictly in UTC format when published. To allow for both a UTC and local time mindset, each record contains a "ts" field and "datetime" field. The "ts" field is a epoch value and the "datetime" represents the converted local time. 

Under normal circumstances, each JSONL file will contain 24 lines, one line per hour, starting 23:00 on the night before to 22:00 on the following night. However in DST change days, the number of lines will vary to just 23 in spring when the clocks jump forward, skipping an hour and 25 lines in winter when the clock rolls back and repeats an hour.

The following examples highlight this behaviour:

### March 31st 2024 (day is 23 hours long, 1AM skipped)
```json
{"ts": 1711839600, "datetime": "2024/03/30 23:00:00", "market_area": "ROI-DA", "euro": 94.6, "gbp": 80.993}
{"ts": 1711843200, "datetime": "2024/03/31 00:00:00", "market_area": "ROI-DA", "euro": 94.5, "gbp": 80.91}
{"ts": 1711846800, "datetime": "2024/03/31 02:00:00", "market_area": "ROI-DA", "euro": 82.81, "gbp": 70.9}
{"ts": 1711850400, "datetime": "2024/03/31 03:00:00", "market_area": "ROI-DA", "euro": 82.01, "gbp": 70.214}
{"ts": 1711854000, "datetime": "2024/03/31 04:00:00", "market_area": "ROI-DA", "euro": 79, "gbp": 67.637}
{"ts": 1711857600, "datetime": "2024/03/31 05:00:00", "market_area": "ROI-DA", "euro": 70.15, "gbp": 60.06}
{"ts": 1711861200, "datetime": "2024/03/31 06:00:00", "market_area": "ROI-DA", "euro": 71.1, "gbp": 60.873}
{"ts": 1711864800, "datetime": "2024/03/31 07:00:00", "market_area": "ROI-DA", "euro": 73.87, "gbp": 63.245}
{"ts": 1711868400, "datetime": "2024/03/31 08:00:00", "market_area": "ROI-DA", "euro": 78.07, "gbp": 66.841}
{"ts": 1711872000, "datetime": "2024/03/31 09:00:00", "market_area": "ROI-DA", "euro": 82.43, "gbp": 70.57}
{"ts": 1711875600, "datetime": "2024/03/31 10:00:00", "market_area": "ROI-DA", "euro": 78.84, "gbp": 67.5}
{"ts": 1711879200, "datetime": "2024/03/31 11:00:00", "market_area": "ROI-DA", "euro": 73.15, "gbp": 62.628}
{"ts": 1711882800, "datetime": "2024/03/31 12:00:00", "market_area": "ROI-DA", "euro": 69, "gbp": 59.075}
{"ts": 1711886400, "datetime": "2024/03/31 13:00:00", "market_area": "ROI-DA", "euro": 65.2, "gbp": 55.822}
{"ts": 1711890000, "datetime": "2024/03/31 14:00:00", "market_area": "ROI-DA", "euro": 65.2, "gbp": 55.822}
{"ts": 1711893600, "datetime": "2024/03/31 15:00:00", "market_area": "ROI-DA", "euro": 66.9, "gbp": 57.277}
{"ts": 1711897200, "datetime": "2024/03/31 16:00:00", "market_area": "ROI-DA", "euro": 72.45, "gbp": 62.029}
{"ts": 1711900800, "datetime": "2024/03/31 17:00:00", "market_area": "ROI-DA", "euro": 93.44, "gbp": 80}
{"ts": 1711904400, "datetime": "2024/03/31 18:00:00", "market_area": "ROI-DA", "euro": 111.35, "gbp": 95.334}
{"ts": 1711908000, "datetime": "2024/03/31 19:00:00", "market_area": "ROI-DA", "euro": 125, "gbp": 107.021}
{"ts": 1711911600, "datetime": "2024/03/31 20:00:00", "market_area": "ROI-DA", "euro": 120.51, "gbp": 103.176}
{"ts": 1711915200, "datetime": "2024/03/31 21:00:00", "market_area": "ROI-DA", "euro": 100, "gbp": 85.616}
{"ts": 1711918800, "datetime": "2024/03/31 22:00:00", "market_area": "ROI-DA", "euro": 80.1, "gbp": 68.579}
```

### October 27th 2024 (day is 25 hours long, two 1AM periods)
```json
{"ts": 1729980000, "datetime": "2024/10/26 23:00:00", "market_area": "ROI-DA", "euro": 171.11, "gbp": 142.544}
{"ts": 1729983600, "datetime": "2024/10/27 00:00:00", "market_area": "ROI-DA", "euro": 180.2, "gbp": 150.117}
{"ts": 1729987200, "datetime": "2024/10/27 01:00:00", "market_area": "ROI-DA", "euro": 196.2, "gbp": 163.446}
{"ts": 1729990800, "datetime": "2024/10/27 01:00:00", "market_area": "ROI-DA", "euro": 203, "gbp": 169.11}
{"ts": 1729994400, "datetime": "2024/10/27 02:00:00", "market_area": "ROI-DA", "euro": 163.6, "gbp": 136.288}
{"ts": 1729998000, "datetime": "2024/10/27 03:00:00", "market_area": "ROI-DA", "euro": 137.93, "gbp": 114.9}
{"ts": 1730001600, "datetime": "2024/10/27 04:00:00", "market_area": "ROI-DA", "euro": 115.45, "gbp": 96.176}
{"ts": 1730005200, "datetime": "2024/10/27 05:00:00", "market_area": "ROI-DA", "euro": 122.01, "gbp": 101.641}
{"ts": 1730008800, "datetime": "2024/10/27 06:00:00", "market_area": "ROI-DA", "euro": 148.45, "gbp": 123.667}
{"ts": 1730012400, "datetime": "2024/10/27 07:00:00", "market_area": "ROI-DA", "euro": 106.45, "gbp": 88.679}
{"ts": 1730016000, "datetime": "2024/10/27 08:00:00", "market_area": "ROI-DA", "euro": 110.07, "gbp": 91.694}
{"ts": 1730019600, "datetime": "2024/10/27 09:00:00", "market_area": "ROI-DA", "euro": 102, "gbp": 84.972}
{"ts": 1730023200, "datetime": "2024/10/27 10:00:00", "market_area": "ROI-DA", "euro": 100.89, "gbp": 84.047}
{"ts": 1730026800, "datetime": "2024/10/27 11:00:00", "market_area": "ROI-DA", "euro": 95, "gbp": 79.14}
{"ts": 1730030400, "datetime": "2024/10/27 12:00:00", "market_area": "ROI-DA", "euro": 93.48, "gbp": 77.874}
{"ts": 1730034000, "datetime": "2024/10/27 13:00:00", "market_area": "ROI-DA", "euro": 100.3, "gbp": 83.555}
{"ts": 1730037600, "datetime": "2024/10/27 14:00:00", "market_area": "ROI-DA", "euro": 96.01, "gbp": 79.982}
{"ts": 1730041200, "datetime": "2024/10/27 15:00:00", "market_area": "ROI-DA", "euro": 102.03, "gbp": 85}
{"ts": 1730044800, "datetime": "2024/10/27 16:00:00", "market_area": "ROI-DA", "euro": 128.01, "gbp": 106.639}
{"ts": 1730048400, "datetime": "2024/10/27 17:00:00", "market_area": "ROI-DA", "euro": 140.43, "gbp": 116.986}
{"ts": 1730052000, "datetime": "2024/10/27 18:00:00", "market_area": "ROI-DA", "euro": 120.56, "gbp": 100.43}
{"ts": 1730055600, "datetime": "2024/10/27 19:00:00", "market_area": "ROI-DA", "euro": 110, "gbp": 91.636}
{"ts": 1730059200, "datetime": "2024/10/27 20:00:00", "market_area": "ROI-DA", "euro": 101.3, "gbp": 84.389}
{"ts": 1730062800, "datetime": "2024/10/27 21:00:00", "market_area": "ROI-DA", "euro": 92.01, "gbp": 76.649}
{"ts": 1730066400, "datetime": "2024/10/27 22:00:00", "market_area": "ROI-DA", "euro": 80.08, "gbp": 66.711}
```
